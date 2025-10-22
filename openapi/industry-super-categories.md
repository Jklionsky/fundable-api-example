# Industry Filter API Documentation - Overview

This documentation provides a complete reference for all available industries organized into logical categories. Use the industry permalinks in your API calls to filter results by specific industries.

## Main Classifications

The industries are organized into four main categories for easier navigation:

### 🏢 Business & Technology
Core business operations, financial services, and technology infrastructure.
- [View Business & Technology Industries →](industry-api-docs-business-tech.md)

### 🛒 Commerce & Consumer  
Customer-facing products, retail, consumer services, and lifestyle.
- [View Commerce & Consumer Industries →](industry-api-docs-commerce-consumer.md)

### 📺 Media & Content
Content creation, publishing, entertainment, and communication.
- [View Media & Content Industries →](industry-api-docs-media-content.md)

### 🔬 Science & Industry
Research, manufacturing, healthcare, and specialized industries.
- [View Science & Industry Industries →](industry-api-docs-science-industry.md)

## Quick Reference - All Super Categories

### Business & Technology Categories
- **Artificial Intelligence (AI)** - `artificial-intelligence-e551`
- **Financial Services** - `financial-services-d7b6`
- **Payments** - `payments-cb33`
- **Blockchain and Cryptocurrency** - `blockchain-and-cryptocurrency`
- **Data and Analytics** - `data-and-analytics`
- **Information Technology** - `information-technology-4fe3`
- **Internet Services** - `internet-services`
- **Software** - `software-85b6`
- **Privacy and Security** - `privacy-and-security`
- **Professional Services** - `professional-services-abe5`
- **Administrative Services** - `administrative-services`
- **Sales and Marketing** - `sales-and-marketing`
- **Advertising** - `advertising-f0bd`
- **Lending and Investments** - `lending-and-investments`
- **Apps** - `apps-2683`
- **Platforms** - `platforms`

### Commerce & Consumer Categories
- **Commerce and Shopping** - `commerce-and-shopping`
- **Consumer Goods** - `consumer-goods-b39a`
- **Consumer Electronics** - `consumer-electronics-52f3`
- **Clothing and Apparel** - `clothing-and-apparel`
- **Food and Beverage** - `food-and-beverage-5f1e`
- **Real Estate** - `real-estate-598c`
- **Travel and Tourism** - `travel-and-tourism`
- **Community and Lifestyle** - `community-and-lifestyle`
- **Events** - `events-7a2a`
- **Gaming** - `gaming-02a6`
- **Mobile** - `mobile-ec09`
- **Transportation** - `transportation-adc3`

### Media & Content Categories
- **Media and Entertainment** - `media-and-entertainment-3bd7`
- **Content and Publishing** - `content-and-publishing`
- **Music and Audio** - `music-and-audio`
- **Video** - `video-d457`
- **Design** - `design`
- **Messaging and Telecommunications** - `messaging-and-telecommunications`
- **Social Impact** - `social-impact-e643`
- **Education** - `education-c9b5`

### Science & Industry Categories
- **Science and Engineering** - `science-and-engineering`
- **Biotechnology** - `biotechnology-0400`
- **Health Care** - `health-care-a53c`
- **Manufacturing** - `manufacturing-133d`
- **Agriculture and Farming** - `agriculture-and-farming`
- **Energy** - `energy-2b83`
- **Sustainability** - `sustainability-5142`
- **Natural Resources** - `natural-resources-26a5`
- **Hardware** - `hardware-2e6e`
- **Navigation and Mapping** - `navigation-and-mapping`
- **Government and Military** - `government-and-military`
- **Sports** - `sports-8f4d`
- **Other** - `other`

## Usage

To filter by industry in your API calls, use the industry permalink as the value for your industry filter parameter. For example:

```
GET /api/v1/deals?industries=artificial-intelligence,fintech-e067,blockchain
GET /api/v1/companies?industries=saas-5c4e,mobile-apps
GET /api/v1/investors?industries=biotechnology,health-care
```

Note that some industries may have similar names but different permalinks (indicated by the suffix codes). Always use the exact permalink shown in the documentation for accurate filtering.

## Navigation

- [Business & Technology →](industry-api-docs-business-tech.md)
- [Commerce & Consumer →](industry-api-docs-commerce-consumer.md)  
- [Media & Content →](industry-api-docs-media-content.md)
- [Science & Industry →](industry-api-docs-science-industry.md)
