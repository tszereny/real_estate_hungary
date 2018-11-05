# Scrape real estates listed in Hungary---# What is it?Python script, which scrapes the largest real estate website in Hungary# FeaturesTwo languages:1. English2. HungarianGetting available real estate types on the website:```pythonfrom real_estate_hungary import remove_spec_hun_chars, RequestWithHeaders, RealEstateHungarySettings, RealEstateHungaryPageListingslanguage='eng'eng_settings=RealEstateHungarySettings(lang=language)```Listing types:```pythoneng_settings.listing_types['for-sale', 'for-rent']```Property types:```pythoneng_settings.property_types['apartment', 'house', 'land', 'garage', 'summer-resort', 'industrial', 'office', 'catering-unit', 'pension']```Setting up page parameters:```pythoncapital_of_hungary='budapest'page_params={'real_estate_hun_settings':eng_settings,            'city':capital_of_hungary,            'listing_type':'for-sale',            'property_type':'apartment',            'page_num':1}real_estates_on_page=RealEstateHungaryPageListings(**page_params)``````pythonprint('Maximum number of pages: {:,}'.format(real_estates_on_page.max_page))print('Maximum number of {property_type}s {listing_type} in {city}: {listings:,}'.format(**{**real_estates_on_page.params, 'listings':real_estates_on_page.max_listing}))Maximum number of pages: 1,116Maximum number of apartments for-sale in budapest: 13,382```Scrape all real estates on the given page:```pythonlistings_eng=real_estates_on_page.listings_to_df()listings_eng.head()```|property_url|city_district|lat|lng|building_material|condition_of_real_estate|area_size	|ground_area_size|price_in_eur|price_in_huf|convenience_level|desc|floors|orientation|ownership_status|type_of_heating||--------|--------|--------|--------|--------|--------|--------|--------|--------	|--------|--------|--------|--------|--------|--------|--------|--------||https://realestate.hu/real-estate/Apartment-fo...	|Budapest, District XIII	|47.525306	|19.068548	|Brick	|Building in progress	|88 square meter	|88 square meter	|209092	|67430000	|NaN	|Translated text Original text PRÉMIUM LAKÁSOK,...	|1st floor	|Yard	|NaN	|In-house with unique meter||https://realestate.hu/real-estate/Apartment-fo...	|Budapest, District III	|47.589843	|19.065879	|Brick	|Building in progress	|85 square meter	|85 square meter	|204397	|65915850	|NaN	|Translated text Original text KÖLTÖZHETŐ APART...	|Ground floor	|NaN	|NaN	|In-house with unique meter||https://realestate.hu/real-estate/Apartment-fo...	|Budapest, District V	|47.509952	|19.053077	|Brick	|Renovated	|83 square meter	|83 square meter	|213650	|68900000	|NaN	|Translated text Original text 5 kerület. Lipót...	|3rd floor	|Street front	|NaN	|Termosifone||https://realestate.hu/real-estate/Apartment-fo...	|Budapest, District VIII	|47.491388	|19.070060	|Brick	|Average	|101 square meter	|101 square meter	|178610	|57600000	|Modern convenience	|Translated text Original text Eladó a Palotane...	|NaN	|NaN	|NaN	|Convector||https://realestate.hu/real-estate/Apartment-fo...	|Budapest, District XI	|47.483772	|19.051580	|Brick	|Good	|129 square meter	|129 square meter	|369004	|119000000	|Modern convenience	|Translated text Original text GELLÉRT DUPLEX L...	|4th floor	|Panoramic	|NaN	|Termosifone|