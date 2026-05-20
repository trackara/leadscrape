"""
config.py — San Canzian Lead Finder
We are EXCLUSIVELY looking for OUTBOUND travel businesses — agencies that
send clients FROM their city TO European destinations.
"""

SEGMENT_QUERIES = {
    "Luxury Tour Operator": [
        "luxury travel agency European destinations portfolio",
        "tailor made luxury travel Europe boutique hotels",
        "Luxusreisebüro Europa Reisen maßgeschneidert",
        "Luxusreiseveranstalter Europa individuell",
        "agence voyage luxe destinations europeennes",
        "agencia viajes lujo destinos europeos",
    ],
    "MICE Agency": [
        "MICE agency Europe meetings incentives conferences events",
        "MICE Agentur Europa Veranstaltungen international",
        "agence MICE Europe evenements",
        "agenzia MICE Europa conferenze incentive",
    ],
    "Incentive Agency": [
        "incentive travel agency Europe corporate reward trips",
        "Incentive Agentur Reisen Europa Ausland Firmen",
        "incentive travel Europe luxury hotels corporate",
        "agence incentive voyage Europe recompense",
    ],
    "Wedding Planner": [
        "destination wedding planner Europe abroad",
        "wedding planner Europe Mediterranean destination",
        "Hochzeitsplaner Ausland Europa Destination Wedding",
        "planificador bodas destino Europa",
    ],
    "Corporate Event Planner": [
        "corporate retreat planner Europe off-site luxury",
        "executive retreat Europe boutique venue planning",
        "Firmenretreat Europa Planung Agentur Ausland",
        "corporate events Europe travel agency",
    ],
    "FIT Tour Operator": [
        "FIT travel agency tailor made Europe individual",
        "individuelle Europareisen Veranstalter FIT",
        "operateur FIT voyage individuel Europe",
        "FIT Reiseveranstalter Europa maßgeschneidert",
    ],
    "Boutique Tour Operator": [
        "boutique tour operator Europe curated travel",
        "boutique Reiseveranstalter Europa",
        "operateur boutique Europe voyage sur mesure",
        "boutique travel agency European hotels",
    ],
    "DMC": [
        "DMC outbound Europe sending clients luxury",
        "destination management company European travel",
        "DMC Europa Reisen outbound luxury",
    ],
    "High-End Travel Advisor": [
        "luxury travel advisor Europe portfolio hotels",
        "travel consultant boutique hotels Europe curated",
        "Reiseberater Luxushotels Europa exklusiv",
        "conseiller voyages luxe Europe hotels selectionnes",
    ],
}

EXISTING_PARTNERS = [
    "slh.com", "Small Luxury Hotels",
    "mrandmrssmith.com", "Mr & Mrs Smith",
    "sovereign.com", "Sovereign Luxury",
    "classictravel.com", "Classic Travel",
    "theluxevoyager.com", "Luxe Voyager",
    "hilton.com", "virtuoso.com",
]

DEFAULT_TARGET_KEYWORDS = [
    "European destinations", "Europareisen", "Auslandsreisen",
    "portfolio", "curated", "preferred hotels", "selection",
    "tailor", "bespoke", "maßgeschneidert", "individuell",
    "luxury", "luxus", "luxe", "lusso",
    "boutique", "premium", "exclusive", "exklusiv",
    "incentive", "MICE", "reward travel",
    "destination wedding", "Hochzeit Ausland",
    "wellness", "spa", "gourmet", "culinary", "wine",
    "Mediterranean", "Adria", "Adriatic", "Croatia", "Kroatien",
    "Istria", "Istrien", "Slovenia", "Italy", "Tuscany",
]

ANTI_KEYWORDS = [
    "inbound", "incoming",
    "stadtführung", "city tour", "guided tour",
    "tagungsraum", "tagungshotel", "konferenzraum", "veranstaltungsraum",
    "event venue", "conference venue", "meeting room",
    "messe", "messestand",
    "cruise", "kreuzfahrt", "party", "youth", "spring break",
    "transfer service", "airport transfer", "limousine service",
    "domestic only", "nur deutschland", "lokal",
]

SUGGESTED_COMPETITORS = [
    "https://maslina.com",
    "https://lesic-dimitri.com",
    "https://www.roxanich.com",
    "https://www.borgoegnazia.com",
    "https://caprocat.com",
    "https://www.lefkasfarm.com",
    "https://www.amanresorts.com/aman-sveti-stefan",
]

DOMAIN_BLACKLIST = [
    "google.", "bing.", "duckduckgo.", "yahoo.",
    "facebook.com", "instagram.com", "linkedin.com",
    "twitter.com", "x.com", "youtube.com", "tiktok.com", "pinterest.",
    "wikipedia.org", "wikidata.org", "reddit.com",
    "tripadvisor.", "yelp.", "trustpilot.", "glassdoor.",
    "booking.com", "expedia.", "hotels.com", "airbnb.",
    "yellowpages.", "foursquare.", "amazon.", "ebay.",
]

UI_STRINGS = {
    "en": {
        "title": "Lead Finder",
        "subtitle": "San Canzian — find outbound travel partners worldwide.",
        "settings": "Settings",
        "results_per_query": "Results per query",
        "enrich_websites": "Enrich from websites",
        "qualification": "Qualification keywords",
        "qual_caption": "One per line — matches boost score",
        "existing_partners": "Existing partners",
        "existing_caption": "Excluded from results",
        "location": "Region or city",
        "location_placeholder": "e.g. Vienna, Austria  ·  Frankfurt  ·  Zurich",
        "segments": "Segments",
        "custom_query": "Custom query (optional)",
        "run": "Run search",
        "err_location": "Enter a region or city.",
        "err_segments": "Pick at least one segment.",
        "found": "Found", "leads_in": "leads in",
        "results": "Results", "total": "Total",
        "qualified": "Qualified", "needs_review": "Needs review", "have_email": "With email",
        "filter_status": "Status", "filter_segment": "Segment",
        "filter_email_only": "Email only",
        "show_existing_partners": "Show existing partners",
        "download_excel": "Download Excel",
        "no_results": "No leads matched your filters.",
        "footer": "Internal use only. B2B contact data only. Always include opt-out in outbound emails.",
        "map_view": "Map view",
        "company": "Company", "fit": "Fit", "status": "Status", "specialization": "Specialization",
    },
    "hr": {
        "title": "Trazilica Partnera",
        "subtitle": "San Canzian — pronalazak outbound partnera diljem svijeta.",
        "settings": "Postavke",
        "results_per_query": "Rezultata po upitu",
        "enrich_websites": "Dohvati kontakte s web stranica",
        "qualification": "Kljucne rijeci za kvalifikaciju",
        "qual_caption": "Jedna po retku — podudaranja povecavaju score",
        "existing_partners": "Postojeci partneri",
        "existing_caption": "Iskljuceni iz rezultata",
        "location": "Regija ili grad",
        "location_placeholder": "npr. Bec  ·  Frankfurt  ·  Zurich",
        "segments": "Segmenti",
        "custom_query": "Vlastiti upit (opcionalno)",
        "run": "Pokreni pretragu",
        "err_location": "Unesi regiju ili grad.",
        "err_segments": "Odaberi barem jedan segment.",
        "found": "Pronadeno", "leads_in": "leadova u",
        "results": "Rezultati", "total": "Ukupno",
        "qualified": "Kvalificirano", "needs_review": "Za pregled", "have_email": "S e-mailom",
        "filter_status": "Status", "filter_segment": "Segment",
        "filter_email_only": "Samo s e-mailom",
        "show_existing_partners": "Prikazi postojece partnere",
        "download_excel": "Preuzmi Excel",
        "no_results": "Nijedan lead ne odgovara filterima.",
        "footer": "Samo za internu upotrebu. Uvijek ukljuci opt-out u outbound mailovima.",
        "map_view": "Karta",
        "company": "Tvrtka", "fit": "Match", "status": "Status", "specialization": "Specijalizacija",
    },
}
