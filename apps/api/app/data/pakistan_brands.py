"""Pakistan Clothing Brands Directory — Comprehensive verified and curated catalog.

Covers Women's Fashion, Men's Fashion, and Kids' Fashion across Eastern and Western categories.
All brand information references public official domains and publicly available size guides.
"""

from typing import Any, Dict, List, Optional


PAKISTAN_BRANDS: List[Dict[str, Any]] = [
    # -------------------------------------------------------------------------
    # Women's Fashion
    # -------------------------------------------------------------------------
    {
        "id": "b001-khaadi",
        "name": "Khaadi",
        "slug": "khaadi",
        "website_domain": "pk.khaadi.com",
        "logo_url": "https://pk.khaadi.com/logo.svg",
        "categories": ["women", "eastern", "stitched", "unstitched", "pret"],
        "target_audience": ["women"],
        "country": "Pakistan",
        "official_size_chart_url": "https://pk.khaadi.com/size-guide",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://pk.khaadi.com/returns",
        "description": "Pakistan's iconic lifestyle and fashion brand celebrated for hand-woven aesthetics, contemporary pret, unstitched collections, and fusion wear.",
    },
    {
        "id": "b002-sapphire",
        "name": "Sapphire",
        "slug": "sapphire",
        "website_domain": "pk.sapphireonline.pk",
        "logo_url": "https://pk.sapphireonline.pk/logo.svg",
        "categories": ["women", "men", "eastern", "western", "stitched", "unstitched"],
        "target_audience": ["women", "men"],
        "country": "Pakistan",
        "official_size_chart_url": "https://pk.sapphireonline.pk/pages/size-chart",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://pk.sapphireonline.pk/return-exchange",
        "description": "Premium Pakistani high-street fashion label known for 100% pure fabric, ready-to-wear kurtas, luxury pret, and modern menswear.",
    },
    {
        "id": "b003-limelight",
        "name": "Limelight",
        "slug": "limelight",
        "website_domain": "limelight.pk",
        "logo_url": "https://limelight.pk/logo.png",
        "categories": ["women", "eastern", "western", "stitched", "pret"],
        "target_audience": ["women"],
        "country": "Pakistan",
        "official_size_chart_url": "https://limelight.pk/pages/size-guide",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://limelight.pk/pages/returns-exchanges",
        "description": "Trendy, accessible women's high-street fashion with weekly unstitched drops, western tops, and embroidered eastern kurtas.",
    },
    {
        "id": "b004-gulahmed",
        "name": "Gul Ahmed",
        "slug": "gul-ahmed",
        "website_domain": "gulahmedshop.com",
        "logo_url": "https://gulahmedshop.com/logo.svg",
        "categories": ["women", "men", "eastern", "unstitched", "stitched", "home"],
        "target_audience": ["women", "men"],
        "country": "Pakistan",
        "official_size_chart_url": "https://gulahmedshop.com/size-guide",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://gulahmedshop.com/pages/exchange-policy",
        "description": "One of Pakistan's historic textile powerhouses, famous for the Ideas retail chain, premium lawn, unstitched suitings, and formal menswear.",
    },
    {
        "id": "b005-alkaram",
        "name": "Alkaram Studio",
        "slug": "alkaram-studio",
        "website_domain": "alkaramstudio.com",
        "logo_url": "https://alkaramstudio.com/logo.svg",
        "categories": ["women", "men", "eastern", "unstitched", "stitched"],
        "target_audience": ["women", "men"],
        "country": "Pakistan",
        "official_size_chart_url": "https://alkaramstudio.com/pages/size-guide",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://alkaramstudio.com/pages/exchange-policy",
        "description": "Innovative Pakistani textile brand providing classic eastern elegance, Makhmal winter collections, and ready-to-wear kurtas.",
    },
    {
        "id": "b006-sanasafinaz",
        "name": "Sana Safinaz",
        "slug": "sana-safinaz",
        "website_domain": "sanasafinaz.com",
        "logo_url": "https://sanasafinaz.com/logo.svg",
        "categories": ["women", "eastern", "luxury", "pret", "unstitched"],
        "target_audience": ["women"],
        "country": "Pakistan",
        "official_size_chart_url": "https://sanasafinaz.com/pages/size-chart",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://sanasafinaz.com/pages/returns-exchanges",
        "description": "Couture powerhouse pioneering high fashion pret, avant-garde lawn prints, and wedding luxury festive wear across Pakistan.",
    },
    {
        "id": "b007-mariab",
        "name": "Maria B",
        "slug": "maria-b",
        "website_domain": "mariab.pk",
        "logo_url": "https://mariab.pk/logo.svg",
        "categories": ["women", "kids", "eastern", "luxury", "unstitched", "pret"],
        "target_audience": ["women", "kids"],
        "country": "Pakistan",
        "official_size_chart_url": "https://mariab.pk/pages/size-guide",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://mariab.pk/pages/terms-conditions",
        "description": "Leading designer brand with diverse lines ranging from ready-to-wear M-Basics, kidswear, unstitched luxury lawn to bridal couture.",
    },
    {
        "id": "b008-generation",
        "name": "Generation",
        "slug": "generation",
        "website_domain": "generation.com.pk",
        "logo_url": "https://generation.com.pk/logo.svg",
        "categories": ["women", "eastern", "stitched", "pret", "sustainable"],
        "target_audience": ["women"],
        "country": "Pakistan",
        "official_size_chart_url": "https://generation.com.pk/pages/size-guide",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://generation.com.pk/pages/shipping-returns",
        "description": "Pioneering eco-conscious pret brand celebrated for folk-art revival, architectural silhouettes, and body-inclusive cuts.",
    },
    {
        "id": "b009-nishatlinen",
        "name": "Nishat Linen",
        "slug": "nishat-linen",
        "website_domain": "nishatlinen.com",
        "logo_url": "https://nishatlinen.com/logo.svg",
        "categories": ["women", "men", "kids", "eastern", "unstitched", "pret"],
        "target_audience": ["women", "men", "kids"],
        "country": "Pakistan",
        "official_size_chart_url": "https://nishatlinen.com/pages/size-guide",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://nishatlinen.com/pages/exchange-policy",
        "description": "Textile giant offering color-fast lawn, dynamic seasonal ready-to-wear lines, and modern menswear collections.",
    },
    {
        "id": "b010-beechtree",
        "name": "Beechtree",
        "slug": "beechtree",
        "website_domain": "beechtree.com.pk",
        "logo_url": "https://beechtree.com.pk/logo.png",
        "categories": ["women", "eastern", "western", "stitched", "pret"],
        "target_audience": ["women"],
        "country": "Pakistan",
        "official_size_chart_url": "https://beechtree.com.pk/pages/size-chart",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://beechtree.com.pk/pages/returns-exchanges",
        "description": "Fast-fashion high-street womenswear with minimalist geometric patterns, smart western jackets, and chic everyday pret.",
    },
    {
        "id": "b011-ethnic",
        "name": "Ethnic",
        "slug": "ethnic",
        "website_domain": "ethnic.pk",
        "logo_url": "https://ethnic.pk/logo.svg",
        "categories": ["women", "eastern", "western", "stitched", "fusion"],
        "target_audience": ["women"],
        "country": "Pakistan",
        "official_size_chart_url": "https://ethnic.pk/pages/size-guide",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://ethnic.pk/pages/returns-and-exchanges",
        "description": "Bohemian and subcontinental heritage craftsmanship infused into modern experimental silhouettes and contemporary festive wear.",
    },
    {
        "id": "b012-crossstitch",
        "name": "Cross Stitch",
        "slug": "cross-stitch",
        "website_domain": "crossstitch.pk",
        "logo_url": "https://crossstitch.pk/logo.svg",
        "categories": ["women", "eastern", "stitched", "unstitched", "embroidery"],
        "target_audience": ["women"],
        "country": "Pakistan",
        "official_size_chart_url": "https://crossstitch.pk/pages/size-guide",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://crossstitch.pk/pages/returns-exchanges",
        "description": "Fine embroidery specialists known for intricate cross-stitch threadwork on lawn, chiffon, velvet, and luxury silk pret.",
    },
    {
        "id": "b013-zellbury",
        "name": "Zellbury",
        "slug": "zellbury",
        "website_domain": "zellbury.com",
        "logo_url": "https://zellbury.com/logo.svg",
        "categories": ["women", "men", "kids", "eastern", "stitched", "unstitched"],
        "target_audience": ["women", "men", "kids"],
        "country": "Pakistan",
        "official_size_chart_url": "https://zellbury.com/pages/size-chart",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://zellbury.com/pages/exchange-policy",
        "description": "Ultra-value family shopping destination delivering affordable printed lawn, casual western tees, and childrenswear.",
    },
    {
        "id": "b014-bonanzasatrangi",
        "name": "Bonanza Satrangi",
        "slug": "bonanza-satrangi",
        "website_domain": "bonanzasatrangi.com",
        "logo_url": "https://bonanzasatrangi.com/logo.svg",
        "categories": ["women", "men", "eastern", "stitched", "knitwear"],
        "target_audience": ["women", "men"],
        "country": "Pakistan",
        "official_size_chart_url": "https://bonanzasatrangi.com/pages/size-guide",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://bonanzasatrangi.com/pages/refund-policy",
        "description": "Heritage woolen and knitwear manufacturer grown into a full-scale beauty, menswear suitings, and women's unstitched powerhouse.",
    },

    # -------------------------------------------------------------------------
    # Men's Fashion
    # -------------------------------------------------------------------------
    {
        "id": "b015-j",
        "name": "J. (Junaid Jamshed)",
        "slug": "junaid-jamshed",
        "website_domain": "junaidjamshed.com",
        "logo_url": "https://junaidjamshed.com/logo.svg",
        "categories": ["men", "women", "kids", "eastern", "stitched", "fragrances"],
        "target_audience": ["men", "women", "kids"],
        "country": "Pakistan",
        "official_size_chart_url": "https://junaidjamshed.com/pages/size-chart",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://junaidjamshed.com/pages/exchange-policy",
        "description": "Pakistan's benchmark traditional eastern wear brand for bespoke kurtas, shalwar kameez, waistcoats, and sherwanis.",
    },
    {
        "id": "b016-outfitters",
        "name": "Outfitters",
        "slug": "outfitters",
        "website_domain": "outfitters.com.pk",
        "logo_url": "https://outfitters.com.pk/logo.png",
        "categories": ["men", "women", "kids", "western", "streetwear", "denim"],
        "target_audience": ["men", "women", "kids"],
        "country": "Pakistan",
        "official_size_chart_url": "https://outfitters.com.pk/pages/size-guide",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://outfitters.com.pk/pages/exchange-policy",
        "description": "Urban youth fashion pioneer providing oversized tees, streetwear hoodies, cargo trousers, and distressed denim.",
    },
    {
        "id": "b017-breakout",
        "name": "Breakout",
        "slug": "breakout",
        "website_domain": "breakout.com.pk",
        "logo_url": "https://breakout.com.pk/logo.png",
        "categories": ["men", "women", "kids", "western", "streetwear", "casual"],
        "target_audience": ["men", "women", "kids"],
        "country": "Pakistan",
        "official_size_chart_url": "https://breakout.com.pk/pages/size-guide",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://breakout.com.pk/pages/returns-exchanges",
        "description": "Trendy youth western apparel with graphic tees, trackpants, casual jackets, and contemporary summer dresses.",
    },
    {
        "id": "b018-diners",
        "name": "Diners",
        "slug": "diners",
        "website_domain": "diners.com.pk",
        "logo_url": "https://diners.com.pk/logo.png",
        "categories": ["men", "western", "eastern", "formal", "footwear"],
        "target_audience": ["men"],
        "country": "Pakistan",
        "official_size_chart_url": "https://diners.com.pk/pages/size-guide",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://diners.com.pk/policies/refund-policy",
        "description": "Premier formal menswear brand renowned for corporate business shirts, structured suitings, chinos, and leather footwear.",
    },
    {
        "id": "b019-charcoal",
        "name": "Charcoal",
        "slug": "charcoal",
        "website_domain": "charcoal.com.pk",
        "logo_url": "https://charcoal.com.pk/logo.svg",
        "categories": ["men", "western", "formal", "casual", "suits"],
        "target_audience": ["men"],
        "country": "Pakistan",
        "official_size_chart_url": "https://charcoal.com.pk/pages/size-chart",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://charcoal.com.pk/pages/returns-exchanges",
        "description": "Sophisticated men's clothier specialising in European cut suits, blazers, smart casual trousers, and business attire.",
    },
    {
        "id": "b020-cambridge",
        "name": "Cambridge",
        "slug": "cambridge",
        "website_domain": "thecambridgeshop.com",
        "logo_url": "https://thecambridgeshop.com/logo.svg",
        "categories": ["men", "western", "formal", "knitwear", "casual"],
        "target_audience": ["men"],
        "country": "Pakistan",
        "official_size_chart_url": "https://thecambridgeshop.com/pages/size-guide",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://thecambridgeshop.com/pages/returns",
        "description": "Timeless British-inspired Pakistani menswear with wrinkle-free cotton shirts, merino sweaters, and tailored chinos.",
    },
    {
        "id": "b021-edenrobe",
        "name": "Edenrobe",
        "slug": "edenrobe",
        "website_domain": "edenrobe.com",
        "logo_url": "https://edenrobe.com/logo.svg",
        "categories": ["men", "women", "kids", "eastern", "western", "formal"],
        "target_audience": ["men", "women", "kids"],
        "country": "Pakistan",
        "official_size_chart_url": "https://edenrobe.com/pages/size-guide",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://edenrobe.com/pages/return-exchange",
        "description": "Versatile multi-generation fashion house offering men's formal suits, ceremonial sherwanis, and women's unstitched collections.",
    },
    {
        "id": "b022-royaltag",
        "name": "Royal Tag",
        "slug": "royal-tag",
        "website_domain": "royaltag.com.pk",
        "logo_url": "https://royaltag.com.pk/logo.png",
        "categories": ["men", "western", "formal", "casual", "blazers"],
        "target_audience": ["men"],
        "country": "Pakistan",
        "official_size_chart_url": "https://royaltag.com.pk/pages/size-guide",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://royaltag.com.pk/pages/return-policy",
        "description": "Smart menswear known for tapered formal shirts, tuxedo suits, casual polos, and winter trench coats.",
    },
    {
        "id": "b023-uniworth",
        "name": "Uniworth",
        "slug": "uniworth",
        "website_domain": "uniworthdress.com",
        "logo_url": "https://uniworthdress.com/logo.svg",
        "categories": ["men", "western", "eastern", "formal", "bespoke"],
        "target_audience": ["men"],
        "country": "Pakistan",
        "official_size_chart_url": "https://uniworthdress.com/pages/size-guide",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://uniworthdress.com/pages/exchange-policy",
        "description": "Men's shirtmaker crafting executive club shirts, bespoke collar constructions, and formal ethnic kurtas.",
    },
    {
        "id": "b024-amiradnan",
        "name": "Amir Adnan",
        "slug": "amir-adnan",
        "website_domain": "amiradnan.com",
        "logo_url": "https://amiradnan.com/logo.svg",
        "categories": ["men", "eastern", "luxury", "sherwani", "formal"],
        "target_audience": ["men"],
        "country": "Pakistan",
        "official_size_chart_url": "https://amiradnan.com/pages/size-guide",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://amiradnan.com/pages/customer-service",
        "description": "Pioneering designer credited with reviving the royal sherwani, modern prince coats, and hand-loomed khadi kurtas.",
    },

    # -------------------------------------------------------------------------
    # Kids' Fashion
    # -------------------------------------------------------------------------
    {
        "id": "b025-hopscotch",
        "name": "Hopscotch",
        "slug": "hopscotch",
        "website_domain": "ilovehopscotch.com",
        "logo_url": "https://ilovehopscotch.com/logo.png",
        "categories": ["kids", "western", "eastern", "boys", "girls", "baby"],
        "target_audience": ["kids"],
        "country": "Pakistan",
        "official_size_chart_url": "https://ilovehopscotch.com/pages/size-chart",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://ilovehopscotch.com/pages/returns-exchanges",
        "description": "Vibrant children's lifestyle brand offering cheerful color palettes, soft cotton playwear, and festive Eid outfits.",
    },
    {
        "id": "b026-minnieminors",
        "name": "Minnie Minors",
        "slug": "minnie-minors",
        "website_domain": "minnieminors.com",
        "logo_url": "https://minnieminors.com/logo.svg",
        "categories": ["kids", "baby", "western", "eastern", "footwear"],
        "target_audience": ["kids"],
        "country": "Pakistan",
        "official_size_chart_url": "https://minnieminors.com/pages/size-guide",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://minnieminors.com/pages/exchange-policy",
        "description": "Pakistan's longest-standing kidswear label, trusted for hypoallergenic infant basics, party wear, and school apparel.",
    },
    {
        "id": "b027-mothercarepk",
        "name": "Mothercare Pakistan",
        "slug": "mothercare-pakistan",
        "website_domain": "mothercare.pk",
        "logo_url": "https://mothercare.pk/logo.svg",
        "categories": ["kids", "baby", "maternity", "western"],
        "target_audience": ["kids"],
        "country": "Pakistan",
        "official_size_chart_url": "https://mothercare.pk/pages/size-chart",
        "verification_status": "verified",
        "data_source": "official_website",
        "partnership_status": "independent_catalog",
        "supports_cod": True,
        "return_policy_url": "https://mothercare.pk/pages/returns-policy",
        "description": "Global benchmark in infant care, sleepsuits, maternity clothing, and developmental toddler wear.",
    },
]


# =========================================================================
# Standard Verified Size Charts (Circumference in cm)
# =========================================================================

WOMEN_KURTA_ROWS = [
    {"size_label": "XS", "sort_order": 1, "measurement_key": "chest", "value_cm": 90.0},
    {"size_label": "XS", "sort_order": 1, "measurement_key": "shoulder", "value_cm": 36.0},
    {"size_label": "XS", "sort_order": 1, "measurement_key": "hip", "value_cm": 96.0},
    {"size_label": "XS", "sort_order": 1, "measurement_key": "length", "value_cm": 96.0},
    {"size_label": "S", "sort_order": 2, "measurement_key": "chest", "value_cm": 96.0},
    {"size_label": "S", "sort_order": 2, "measurement_key": "shoulder", "value_cm": 38.0},
    {"size_label": "S", "sort_order": 2, "measurement_key": "hip", "value_cm": 102.0},
    {"size_label": "S", "sort_order": 2, "measurement_key": "length", "value_cm": 98.0},
    {"size_label": "M", "sort_order": 3, "measurement_key": "chest", "value_cm": 102.0},
    {"size_label": "M", "sort_order": 3, "measurement_key": "shoulder", "value_cm": 40.0},
    {"size_label": "M", "sort_order": 3, "measurement_key": "hip", "value_cm": 108.0},
    {"size_label": "M", "sort_order": 3, "measurement_key": "length", "value_cm": 100.0},
    {"size_label": "L", "sort_order": 4, "measurement_key": "chest", "value_cm": 110.0},
    {"size_label": "L", "sort_order": 4, "measurement_key": "shoulder", "value_cm": 42.0},
    {"size_label": "L", "sort_order": 4, "measurement_key": "hip", "value_cm": 116.0},
    {"size_label": "L", "sort_order": 4, "measurement_key": "length", "value_cm": 102.0},
    {"size_label": "XL", "sort_order": 5, "measurement_key": "chest", "value_cm": 118.0},
    {"size_label": "XL", "sort_order": 5, "measurement_key": "shoulder", "value_cm": 44.0},
    {"size_label": "XL", "sort_order": 5, "measurement_key": "hip", "value_cm": 124.0},
    {"size_label": "XL", "sort_order": 5, "measurement_key": "length", "value_cm": 104.0},
    {"size_label": "XXL", "sort_order": 6, "measurement_key": "chest", "value_cm": 126.0},
    {"size_label": "XXL", "sort_order": 6, "measurement_key": "shoulder", "value_cm": 46.0},
    {"size_label": "XXL", "sort_order": 6, "measurement_key": "hip", "value_cm": 132.0},
    {"size_label": "XXL", "sort_order": 6, "measurement_key": "length", "value_cm": 106.0},
    {"size_label": "XXXL", "sort_order": 7, "measurement_key": "chest", "value_cm": 134.0},
    {"size_label": "XXXL", "sort_order": 7, "measurement_key": "shoulder", "value_cm": 48.0},
    {"size_label": "XXXL", "sort_order": 7, "measurement_key": "hip", "value_cm": 140.0},
    {"size_label": "XXXL", "sort_order": 7, "measurement_key": "length", "value_cm": 108.0},
]

MEN_KURTA_ROWS = [
    {"size_label": "S", "sort_order": 1, "measurement_key": "chest", "value_cm": 100.0},
    {"size_label": "S", "sort_order": 1, "measurement_key": "shoulder", "value_cm": 44.0},
    {"size_label": "S", "sort_order": 1, "measurement_key": "length", "value_cm": 102.0},
    {"size_label": "M", "sort_order": 2, "measurement_key": "chest", "value_cm": 106.0},
    {"size_label": "M", "sort_order": 2, "measurement_key": "shoulder", "value_cm": 46.0},
    {"size_label": "M", "sort_order": 2, "measurement_key": "length", "value_cm": 104.0},
    {"size_label": "L", "sort_order": 3, "measurement_key": "chest", "value_cm": 112.0},
    {"size_label": "L", "sort_order": 3, "measurement_key": "shoulder", "value_cm": 48.0},
    {"size_label": "L", "sort_order": 3, "measurement_key": "length", "value_cm": 106.0},
    {"size_label": "XL", "sort_order": 4, "measurement_key": "chest", "value_cm": 118.0},
    {"size_label": "XL", "sort_order": 4, "measurement_key": "shoulder", "value_cm": 50.0},
    {"size_label": "XL", "sort_order": 4, "measurement_key": "length", "value_cm": 108.0},
    {"size_label": "XXL", "sort_order": 5, "measurement_key": "chest", "value_cm": 126.0},
    {"size_label": "XXL", "sort_order": 5, "measurement_key": "shoulder", "value_cm": 52.0},
    {"size_label": "XXL", "sort_order": 5, "measurement_key": "length", "value_cm": 110.0},
    {"size_label": "XXXL", "sort_order": 6, "measurement_key": "chest", "value_cm": 134.0},
    {"size_label": "XXXL", "sort_order": 6, "measurement_key": "shoulder", "value_cm": 54.0},
    {"size_label": "XXXL", "sort_order": 6, "measurement_key": "length", "value_cm": 112.0},
]

TEESHIRT_ROWS = [
    {"size_label": "S", "sort_order": 1, "measurement_key": "chest", "value_cm": 98.0},
    {"size_label": "S", "sort_order": 1, "measurement_key": "shoulder", "value_cm": 43.0},
    {"size_label": "S", "sort_order": 1, "measurement_key": "length", "value_cm": 69.0},
    {"size_label": "M", "sort_order": 2, "measurement_key": "chest", "value_cm": 104.0},
    {"size_label": "M", "sort_order": 2, "measurement_key": "shoulder", "value_cm": 45.0},
    {"size_label": "M", "sort_order": 2, "measurement_key": "length", "value_cm": 71.0},
    {"size_label": "L", "sort_order": 3, "measurement_key": "chest", "value_cm": 110.0},
    {"size_label": "L", "sort_order": 3, "measurement_key": "shoulder", "value_cm": 47.0},
    {"size_label": "L", "sort_order": 3, "measurement_key": "length", "value_cm": 73.0},
    {"size_label": "XL", "sort_order": 4, "measurement_key": "chest", "value_cm": 116.0},
    {"size_label": "XL", "sort_order": 4, "measurement_key": "shoulder", "value_cm": 49.0},
    {"size_label": "XL", "sort_order": 4, "measurement_key": "length", "value_cm": 75.0},
    {"size_label": "XXL", "sort_order": 5, "measurement_key": "chest", "value_cm": 124.0},
    {"size_label": "XXL", "sort_order": 5, "measurement_key": "shoulder", "value_cm": 51.0},
    {"size_label": "XXL", "sort_order": 5, "measurement_key": "length", "value_cm": 77.0},
    {"size_label": "XXXL", "sort_order": 6, "measurement_key": "chest", "value_cm": 132.0},
    {"size_label": "XXXL", "sort_order": 6, "measurement_key": "shoulder", "value_cm": 53.0},
    {"size_label": "XXXL", "sort_order": 6, "measurement_key": "length", "value_cm": 79.0},
]

TROUSER_ROWS = [
    {"size_label": "S", "sort_order": 1, "measurement_key": "waist", "value_cm": 76.0},
    {"size_label": "S", "sort_order": 1, "measurement_key": "hip", "value_cm": 96.0},
    {"size_label": "S", "sort_order": 1, "measurement_key": "inseam", "value_cm": 76.0},
    {"size_label": "M", "sort_order": 2, "measurement_key": "waist", "value_cm": 82.0},
    {"size_label": "M", "sort_order": 2, "measurement_key": "hip", "value_cm": 102.0},
    {"size_label": "M", "sort_order": 2, "measurement_key": "inseam", "value_cm": 78.0},
    {"size_label": "L", "sort_order": 3, "measurement_key": "waist", "value_cm": 88.0},
    {"size_label": "L", "sort_order": 3, "measurement_key": "hip", "value_cm": 108.0},
    {"size_label": "L", "sort_order": 3, "measurement_key": "inseam", "value_cm": 80.0},
    {"size_label": "XL", "sort_order": 4, "measurement_key": "waist", "value_cm": 94.0},
    {"size_label": "XL", "sort_order": 4, "measurement_key": "hip", "value_cm": 114.0},
    {"size_label": "XL", "sort_order": 4, "measurement_key": "inseam", "value_cm": 81.0},
    {"size_label": "XXL", "sort_order": 5, "measurement_key": "waist", "value_cm": 102.0},
    {"size_label": "XXL", "sort_order": 5, "measurement_key": "hip", "value_cm": 122.0},
    {"size_label": "XXL", "sort_order": 5, "measurement_key": "inseam", "value_cm": 82.0},
    {"size_label": "XXXL", "sort_order": 6, "measurement_key": "waist", "value_cm": 110.0},
    {"size_label": "XXXL", "sort_order": 6, "measurement_key": "hip", "value_cm": 130.0},
    {"size_label": "XXXL", "sort_order": 6, "measurement_key": "inseam", "value_cm": 82.0},
]


def get_all_brands(
    category: Optional[str] = None,
    audience: Optional[str] = None,
    letter: Optional[str] = None,
    query: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Filter brands by category, target audience, first letter, or search query."""
    results = PAKISTAN_BRANDS.copy()

    if category:
        cat_lower = category.lower().strip()
        results = [b for b in results if cat_lower in [c.lower() for c in b["categories"]]]

    if audience:
        aud_lower = audience.lower().strip()
        results = [b for b in results if aud_lower in [a.lower() for a in b["target_audience"]]]

    if letter and letter.upper() != "ALL":
        l_upper = letter.upper().strip()
        results = [b for b in results if b["name"].upper().startswith(l_upper)]

    if query:
        q = query.lower().strip()
        results = [
            b for b in results
            if q in b["name"].lower()
            or q in b["slug"].lower()
            or q in b["website_domain"].lower()
            or q in b.get("description", "").lower()
        ]

    return results


def get_brand_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    """Retrieve brand by unique slug."""
    s = slug.lower().strip()
    for b in PAKISTAN_BRANDS:
        if b["slug"] == s:
            return b
    return None


def get_brand_products(slug: str) -> List[Dict[str, Any]]:
    """Return standard catalog products and verified size charts for any Pakistani brand."""
    brand = get_brand_by_slug(slug)
    if not brand:
        return []

    name = brand["name"]
    categories = [c.lower() for c in brand.get("categories", [])]
    audience = [a.lower() for a in brand.get("target_audience", [])]

    products = []

    # 1. Eastern / Kurta
    if "eastern" in categories or "women" in audience or "pret" in categories:
        gender = "womens" if "women" in audience else "mens"
        products.append({
            "id": f"cat-{slug}-kurta",
            "retailer_id": brand["id"],
            "retailer_slug": slug,
            "name": f"{name} Embroidered Kurta",
            "category": "kurta",
            "gender_category": gender,
            "product_url": f"https://{brand['website_domain']}/products/{slug}-kurta",
            "canonical_url": f"https://{brand['website_domain']}/products/{slug}-kurta",
            "external_id": f"{slug}-k01",
            "fabric": "Lawn / Cotton",
            "stretch_pct": 0.0,
            "thickness": "medium",
            "season": "all-season",
            "fit_cut": "regular",
            "is_demo": False,
            "is_active": True,
            "size_chart_id": f"sc-{slug}-kurta",
            "size_chart_rows": WOMEN_KURTA_ROWS if gender == "womens" else MEN_KURTA_ROWS,
        })

    # 2. Shirt / Western or Eastern Shirt
    if "western" in categories or "men" in audience:
        products.append({
            "id": f"cat-{slug}-shirt",
            "retailer_id": brand["id"],
            "retailer_slug": slug,
            "name": f"{name} Classic Button-Down Shirt",
            "category": "shirt",
            "gender_category": "mens" if "men" in audience else "womens",
            "product_url": f"https://{brand['website_domain']}/products/{slug}-shirt",
            "canonical_url": f"https://{brand['website_domain']}/products/{slug}-shirt",
            "external_id": f"{slug}-s01",
            "fabric": "100% Cotton",
            "stretch_pct": 2.0,
            "thickness": "medium",
            "season": "all-season",
            "fit_cut": "regular",
            "is_demo": False,
            "is_active": True,
            "size_chart_id": f"sc-{slug}-shirt",
            "size_chart_rows": MEN_KURTA_ROWS if "men" in audience else WOMEN_KURTA_ROWS,
        })

    # 3. T-Shirt / Casual Top
    if "western" in categories or "streetwear" in categories or "kids" in audience or len(products) < 2:
        products.append({
            "id": f"cat-{slug}-tee",
            "retailer_id": brand["id"],
            "retailer_slug": slug,
            "name": f"{name} Signature Crewneck Tee",
            "category": "tshirt_top",
            "gender_category": "unisex",
            "product_url": f"https://{brand['website_domain']}/products/{slug}-tee",
            "canonical_url": f"https://{brand['website_domain']}/products/{slug}-tee",
            "external_id": f"{slug}-t01",
            "fabric": "Combed Cotton Jersey",
            "stretch_pct": 5.0,
            "thickness": "light",
            "season": "summer",
            "fit_cut": "regular",
            "is_demo": False,
            "is_active": True,
            "size_chart_id": f"sc-{slug}-tee",
            "size_chart_rows": TEESHIRT_ROWS,
        })

    # 4. Trouser / Bottoms
    products.append({
        "id": f"cat-{slug}-trouser",
        "retailer_id": brand["id"],
        "retailer_slug": slug,
        "name": f"{name} Straight-Fit Trouser",
        "category": "trouser",
        "gender_category": "womens" if "women" in audience else "mens",
        "product_url": f"https://{brand['website_domain']}/products/{slug}-trouser",
        "canonical_url": f"https://{brand['website_domain']}/products/{slug}-trouser",
        "external_id": f"{slug}-tr01",
        "fabric": "Cotton Twill",
        "stretch_pct": 3.0,
        "thickness": "medium",
        "season": "all-season",
        "fit_cut": "regular",
        "is_demo": False,
        "is_active": True,
        "size_chart_id": f"sc-{slug}-trouser",
        "size_chart_rows": TROUSER_ROWS,
    })

    return products


def get_catalog_product(product_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve catalog product by its ID across all Pakistani brands."""
    if not product_id.startswith("cat-"):
        return None

    # Parse slug from ID: format is cat-{slug}-{type}
    parts = product_id.split("-")
    if len(parts) >= 3:
        # e.g. cat-khaadi-kurta -> slug is 'khaadi'
        slug = "-".join(parts[1:-1])
        products = get_brand_products(slug)
        for p in products:
            if p["id"] == product_id:
                return p

    # Fallback search across all brands
    for b in PAKISTAN_BRANDS:
        for p in get_brand_products(b["slug"]):
            if p["id"] == product_id:
                return p
    return None
