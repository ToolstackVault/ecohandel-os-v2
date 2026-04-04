#!/usr/bin/env python3
"""
EcoHandel Google Ads PMax Weekly Performance Report
Runs every Monday 08:00 AM via launchd/cron.
Fetches performance data from Google Ads API v23 and prints a formatted report.
"""

import sys
import os
sys.path.insert(0, '/Users/ecohandel.nl/.openclaw/workspace')
os.chdir('/Users/ecohandel.nl/.openclaw/workspace')

from datetime import datetime, timedelta
import google.ads.googleads.client

GOOGLEADS_YAML = '/Users/ecohandel.nl/.openclaw/workspace/secrets/google-ads.yaml'
CUSTOMER_ID = '5921907188'

def format_micros(micros):
    if micros is None:
        return '€0.00'
    return f'€{micros / 1_000_000:.2f}'

def main():
    print(f"\n{'='*60}")
    print(f"  📊 ECOHANDEL GOOGLE ADS PMax REPORT")
    print(f"  {datetime.now().strftime('%A %d %B %Y, %H:%M')}")
    print(f"{'='*60}\n")

    try:
        googleads_client = google.ads.googleads.client.GoogleAdsClient.load_from_storage(path=GOOGLEADS_YAML)
        google_ads_service = googleads_client.get_service("GoogleAdsService")
    except Exception as e:
        print(f"❌ Failed to initialize Google Ads client: {e}")
        sys.exit(1)

    # Campaign-level performance (last 7 days)
    campaign_query = """
    SELECT campaign.id, campaign.name, campaign.status, campaign.advertising_channel_type,
           metrics.impressions, metrics.clicks, metrics.cost_micros,
           metrics.conversions, metrics.all_conversions_value,
           metrics.average_cpc, metrics.ctr
    FROM campaign
    WHERE campaign.status = 'ENABLED'
      AND campaign.advertising_channel_type = 'PERFORMANCE_MAX'
    """

    # Asset group performance (last 7 days) - no aliases, no campaign.id reference
    assetgroup_query = """
    SELECT asset_group.id, asset_group.name, asset_group.status,
           metrics.impressions, metrics.clicks, metrics.cost_micros,
           metrics.conversions
    FROM asset_group
    WHERE asset_group.status = 'ENABLED'
    """

    print("### CAMPAGNES (PMax)\n")
    print(f"{'Campagne':<35} {'Impr.':>8} {'Clicks':>7} {'CTR':>6} {'Kosten':>10} {'CPC':>8} {'Conv.':>7} {'CPA':>8}")
    print("-" * 100)

    try:
        response = google_ads_service.search(customer_id=CUSTOMER_ID, query=campaign_query)
        total_cost = 0
        total_conversions = 0
        total_clicks = 0
        total_impressions = 0

        for row in response:
            c = row.campaign
            m = row.metrics
            cost = m.cost_micros / 1_000_000 if m.cost_micros else 0
            cpc = m.average_cpc / 1_000_000 if m.average_cpc else 0
            ctr = m.ctr * 100 if m.ctr else 0
            conv = m.conversions if m.conversions else 0
            cpa = cost / conv if conv > 0 else 0

            total_cost += cost
            total_conversions += conv
            total_clicks += m.clicks if m.clicks else 0
            total_impressions += m.impressions if m.impressions else 0

            print(f"{c.name:<35} {m.impressions or 0:>8,} {m.clicks or 0:>7,} {ctr:>5.1f}% {format_micros(m.cost_micros):>10} {format_micros(int(m.average_cpc)) if m.average_cpc else '€0.00':>8} {conv:>7.1f} {format_micros(int(cpa * 1_000_000)) if cpa > 0 else '€0.00':>8}")

        print("-" * 100)
        overall_ctr = total_clicks / total_impressions * 100 if total_impressions else 0
        overall_cpa = total_cost / total_conversions if total_conversions else 0
        overall_cpc = total_cost / total_clicks if total_clicks else 0

        print(f"{'TOTAAL':<35} {total_impressions:>8,} {total_clicks:>7,} {overall_ctr:>5.1f}% {format_micros(int(total_cost*1_000_000)):>10} {format_micros(int(overall_cpc*1_000_000)):>8} {total_conversions:>7.1f} {format_micros(int(overall_cpa*1_000_000)):>8}")
        print()
    except Exception as e:
        print(f"⚠️  Campaign query error: {e}")

    print("\n### ASSET GROUPS\n")
    print(f"{'Asset Group':<30} {'Impr.':>8} {'Clicks':>7} {'Kosten':>10} {'Conv.':>7} {'CPA':>8}")
    print("-" * 75)

    try:
        response = google_ads_service.search(customer_id=CUSTOMER_ID, query=assetgroup_query)
        for row in response:
            ag = row.asset_group
            m = row.metrics
            cost = m.cost_micros / 1_000_000 if m.cost_micros else 0
            conv = m.conversions if m.conversions else 0
            cpa = cost / conv if conv > 0 else 0

            print(f"{ag.name:<30} {m.impressions or 0:>8,} {m.clicks or 0:>7,} {format_micros(m.cost_micros):>10} {conv:>7.1f} {format_micros(int(cpa * 1_000_000)) if cpa > 0 else '€—':>8}")
        print()
    except Exception as e:
        print(f"⚠️  Asset group query error: {e}")

    print(f"{'='*60}")
    print(f"  Generated: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
