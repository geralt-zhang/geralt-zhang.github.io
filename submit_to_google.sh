#!/bin/bash

# Google Indexing API submission script
# Requires: API key and OAuth setup

SITE_URL="https://zhehuaf.github.io"

# List of important URLs to submit
URLS=(
    "$SITE_URL/"
    "$SITE_URL/about/"
    "$SITE_URL/blob/"
    "$SITE_URL/blob/2026/mail_client/"
    "$SITE_URL/blob/2026/llm/"
    "$SITE_URL/blob/2026/docker/"
    "$SITE_URL/blob/2026/alu/"
    "$SITE_URL/blob/2026/xv6_lab0_util/"
    "$SITE_URL/blob/2026/xv6_lab1_syscall/"
)

echo "Submitting URLs to Google for indexing..."

# Method 1: Manual submission links
for url in "${URLS[@]}"; do
    echo "Submit manually: https://search.google.com/search-console/url-inspection?resource_id=$SITE_URL&item_key=$url"
done

echo ""
echo "Next steps:"
echo "1. Set up Google Search Console: https://search.google.com/search-console"
echo "2. Verify ownership using google253be4ff0b886db8.html"
echo "3. Submit sitemap.xml"
echo "4. Use URL Inspection tool for individual pages"
