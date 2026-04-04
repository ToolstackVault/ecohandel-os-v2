<?php
declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['ok' => false, 'error' => 'method_not_allowed']);
    exit;
}

$raw = file_get_contents('php://input');
$data = json_decode($raw ?: '{}', true);
if (!is_array($data)) {
    $data = [];
}

function clean(?string $value): string {
    return trim((string)($value ?? ''));
}

function brevo_notify(array $payload): void {
    $apiKey = getenv('BREVO_API_KEY') ?: '';
    $subjectName = $payload['naam'] ?: 'Onbekend';
    $subjectEmail = $payload['email'] ?: 'geen email';
    $subject = 'Nieuwe partner aanvraag — ' . $subjectName;

    $html = '<html><body style="font-family:Arial,sans-serif;color:#1a1a1a">'
        . '<h2 style="margin:0 0 16px">Nieuwe partner aanvraag</h2>'
        . '<p><strong>Naam:</strong> ' . htmlspecialchars($payload['naam'] ?: '—') . '</p>'
        . '<p><strong>Email:</strong> ' . htmlspecialchars($payload['email'] ?: '—') . '</p>'
        . '<p><strong>Telefoon:</strong> ' . htmlspecialchars($payload['telefoon'] ?: '—') . '</p>'
        . '<p><strong>Bron:</strong> ' . htmlspecialchars($payload['bron'] ?: '—') . '</p>'
        . '<p><strong>Campagne:</strong> ' . htmlspecialchars($payload['campaign'] ?: '—') . '</p>'
        . '<p><strong>Bedrijf:</strong> ' . htmlspecialchars($payload['bedrijf'] ?: '—') . '</p>'
        . '<p><strong>Tijdstip:</strong> ' . htmlspecialchars($payload['received_at'] ?: '—') . '</p>'
        . '<p><strong>IP:</strong> ' . htmlspecialchars($payload['ip'] ?: '—') . '</p>'
        . '<p><strong>Referrer:</strong> ' . htmlspecialchars($payload['referrer'] ?: '—') . '</p>'
        . '<hr><p style="color:#666">Actie: neem contact op met ' . htmlspecialchars($subjectEmail) . '</p>'
        . '</body></html>';

    $body = json_encode([
        'sender' => ['name' => 'EcoHandel.nl', 'email' => 'info@ecohandel.nl'],
        'to' => [['email' => 'info@ecohandel.nl', 'name' => 'EcoHandel.nl']],
        'replyTo' => ['email' => 'info@ecohandel.nl', 'name' => 'EcoHandel.nl'],
        'subject' => $subject,
        'htmlContent' => $html,
        'tags' => ['partner-aanvraag'],
        'headers' => ['X-Mailin-Tag' => 'partner-aanvraag'],
    ], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);

    $ch = curl_init('https://api.brevo.com/v3/smtp/email');
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER => [
            'accept: application/json',
            'content-type: application/json',
            'api-key: ' . $apiKey,
        ],
        CURLOPT_POSTFIELDS => $body,
        CURLOPT_TIMEOUT => 20,
    ]);
    curl_exec($ch);
    curl_close($ch);
}

$eventType = clean($data['event_type'] ?? 'partner_request');
$email = strtolower(clean($data['email'] ?? ''));
$naam = clean($data['naam'] ?? '');
$telefoon = clean($data['telefoon'] ?? '');
$bron = clean($data['bron'] ?? 'direct');
$campaign = clean($data['campaign'] ?? 'direct');
$bedrijf = clean($data['bedrijf'] ?? '');
$requestId = bin2hex(random_bytes(8));
$receivedAt = gmdate('c');

$payload = [
    'request_id' => $requestId,
    'event_type' => $eventType,
    'received_at' => $receivedAt,
    'email' => $email,
    'naam' => $naam,
    'telefoon' => $telefoon,
    'bron' => $bron,
    'campaign' => $campaign,
    'bedrijf' => $bedrijf,
    'ip' => $_SERVER['REMOTE_ADDR'] ?? '',
    'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? '',
    'referrer' => $_SERVER['HTTP_REFERER'] ?? '',
];

$baseDir = '/var/www/html/control.ecohandel.nl';
$dataDir = $baseDir . '/data';
if (!is_dir($dataDir)) {
    mkdir($dataDir, 0755, true);
}
$logFile = $dataDir . '/partner-aanvragen.ndjson';
file_put_contents($logFile, json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . PHP_EOL, FILE_APPEND | LOCK_EX);

if ($eventType === 'partner_request') {
    brevo_notify($payload);
}

echo json_encode(['ok' => true, 'request_id' => $requestId, 'event_type' => $eventType]);
