import urllib
import json
import os
from urllib.error import HTTPError
import bs4
import html5lib
import datetime
import numpy as np
import pandas as pd
import re
import certifi

def remove_spec_chars(s):
    SPECIAL='äáéíóőúüű'
    ASCII = 'aaeioouuu'
    transtab = str.maketrans(SPECIAL, ASCII)
    spec_chars_free=s.translate(transtab)
    return spec_chars_free

class RequestWithHeaders:
    '''
    Sending a HTTP request to the given url and parsing the HTML response with the given headers.

    Parameters
    ----------
    url: string
    
    Returns
    -------
    bs4.BeautifulSoup
    
    Examples
    --------
    >>> parsed_html=parse_to_html('https://www.python.org/dev/peps/pep-0020/')
    >>> parsed_html.find(name='h1', class_='page-title')
    <h1 class="page-title">PEP 20 -- The Zen of Python</h1>
    
    '''
    def __init__(self, url, headers=None):
        self.url=url
        self.headers=headers  
    
    @property
    def headers(self):
        return self._headers
    
    @headers.setter
    def headers(self, headers):
        if headers is None:
            default_user_agent='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
            headers={'User-Agent': default_user_agent}
        self._headers=headers
    
    @staticmethod
    def get_http_resp_cont(url, headers):
        http_req=urllib.request.Request(url, headers=headers)
        byte_resp = urllib.request.urlopen(http_req, cafile=certifi.where())
        content = byte_resp.read()
        return content

    def download(self, file_path):
        content = self.get_http_resp_cont(self.url, headers=self.headers)
        with open(file_path, 'wb') as f:
            f.write(content)
    
    def parse_to_html(self, parser=None):
        content = self.get_http_resp_cont(self.url, headers=self.headers)
        if parser is None:
            parser='html5lib'
        parsed_bs_html=bs4.BeautifulSoup(content, parser)
        return parsed_bs_html

class RealEstateHungarySettings:
    '''
    Initialize an object to retrieve the available real estates in Hungary.
    
    Parameters
    ----------
    lang : string
        Language of the requested real estate website in Hungary.
    '''
    def __init__(self, lang):
        self.lang=lang.lower()
        URL_LANG={'hun': 'https://ingatlan.com/', 'eng':'https://realestate.hu/'}
        try:
            self.url=URL_LANG[self.lang]
        except KeyError:
            available_langs=", ".join(URL_LANG.keys())
            raise KeyError('Please specify one of the following languages: {}'.format(available_langs))
        self.parsed_html=RequestWithHeaders(url=self.url).parse_to_html()
        
    def __repr__(self):
        return self.url
    
    @property
    def property_types(self):
        if self.lang=='eng':
            property_types_selector=self.parsed_html.find_all(name='select', class_='input-type')[0]
            propert_types=[tp['value'] for tp in property_types_selector.find_all('option') if len(tp['value'])>0]
        elif self.lang=='hun':
            property_types_selector=self.parsed_html.find(name='select', class_='search-filter-select search-filter-select-long')
            propert_types=[tp['value'] for tp in property_types_selector.find_all('option') if len(tp['value'])>0]
        return propert_types
    
    @property
    def listing_types(self):
        if self.lang=='eng':
            listing_types_selector=self.parsed_html.find_all(name='select', class_='input-type')[1]
            listing_types=[tp['value'] for tp in listing_types_selector.find_all('option') if len(tp['value'])>0]
        elif self.lang=='hun':
            listing_types_selector=self.parsed_html.find(name='div', class_='search-filter-box listing-type')
            listing_types=[tp['value'] for tp in listing_types_selector.find_all('input') if len(tp['value'])>0]
        return listing_types

class RealEstateHungaryPageListings:
    '''
    Initialize an object to extract information of the listed real estates in Hungary on the given page number.
    
    Parameters
    ----------
    real_estate_hun_settings : RealEstateHungarySettings
        Instance of RealEstateHungarySettings, which contains available options for requested language.
    city : string
        City in Hungary.
    listing_type : string
        Purpose of listed real estates, e.g. for sale, for rent.
    property_type : string
        Type of property, e.g. apartment, house etc
    page_num :  int
        Page number on the website
    '''
    def __init__(self, real_estate_hun_settings, city, listing_type, property_type, page_num, photos_dir=None):
        self._real_estate_hun_settings = real_estate_hun_settings
        self.lang = self._real_estate_hun_settings.lang
        self._url = self._real_estate_hun_settings.url
        self.listing_type = listing_type
        self.property_type = property_type
        self.page_num = page_num
        self.photos_dir = photos_dir
        self.city = city
        self.params = {'real_estate_hun_settings': self._real_estate_hun_settings,
                     'city':self.city,
                     'listing_type':self.listing_type,
                     'property_type':self.property_type,
                     'page_num':self.page_num}
        url_map = self.params.copy()
        url_map['url'] = url_map.pop('real_estate_hun_settings').url
        if self.lang == 'eng':
            self._LISTINGS_PER_PAGE = 12
            url_map['listings_per_page'] = self._LISTINGS_PER_PAGE
            self.page_url = '{url}search?location={city}&type={property_type}&sell_type={listing_type}&price[min]=&price[max]=&page={page_num}&per-page={listings_per_page}'.format(**url_map)
        elif self.lang == 'hun':
            self.page_url = '{url}lista/{listing_type}+{property_type}+{city}?page={page_num}'.format(**url_map)
        self.parsed_html = RequestWithHeaders(url=self.page_url).parse_to_html()

    def __repr__(self):
        return self.page_url
        
    @property
    def city(self):
        return self._city
    
    @city.setter
    def city(self, city):
        self._city=remove_spec_chars(city.lower())
    
    @property
    def _real_estate_hun_settings(self):
        return self._real_estate_hun_settings_copy
    
    @_real_estate_hun_settings.setter
    def _real_estate_hun_settings(self, real_estate_hun_settings):
        if not isinstance(real_estate_hun_settings, RealEstateHungarySettings):
            raise BaseException('Please provide an instance of RealEstateHungarySettings class.')       
        self._real_estate_hun_settings_copy=real_estate_hun_settings
    
    @property
    def listing_type(self):
        return self._listing_type
    
    @listing_type.setter
    def listing_type(self, listing_type):
        valid_listing_types=self._real_estate_hun_settings.listing_types
        if listing_type not in valid_listing_types:
            raise BaseException('Please specify one of the following listing types: {}'.format(', '.join(valid_listing_types)))
        self._listing_type=listing_type

    @property
    def property_type(self):
        return self._property_type            

    @property_type.setter
    def property_type(self, property_type):
        valid_property_types=self._real_estate_hun_settings.property_types
        if property_type not in valid_property_types:
            raise BaseException('Please specify one of the following property types: {}'.format(', '.join(valid_property_types)))
        self._property_type=property_type        
        
    @property
    def page_num(self):
        return self._page_num
    
    @page_num.setter
    def page_num(self, page_num):
        try:
            self._page_num=int(page_num)
        except ValueError:
            raise ValueError('Page number must be integer.')
    
    @property
    def max_page(self):
        if self.lang=='eng':
            max_page=np.ceil(self.max_listing/self._LISTINGS_PER_PAGE)
        elif self.lang=='hun':
            pagination=self.parsed_html.find("div",class_="pagination__page-number").get_text().replace(" ", "")
            max_page=pagination.split("/")[1].replace("oldal", "")
        return int(max_page)
    
    @property    
    def max_listing(self):
        if self.lang=='eng':
            max_listing=self.parsed_html.find(name='strong').get_text()
        elif self.lang=='hun':    
            max_listing=self.parsed_html.find("span",class_="filtered_results_count").get_text()
        return int(max_listing)
    
    def extract_attrs(self):
        page_attrs={'lang':self.lang,
                    'listing_type':self.listing_type,
                    'property_type':self.property_type,
                    'page_num':self.page_num,
                    'max_page':self.max_page,
                    'max_listing':self.max_listing}
        return page_attrs

    def get_page_listings(self):
        if self.lang=='eng':
            prop_coll=self.parsed_html.find(name='div', class_='Apartment-Collection row')
            page={
                'property_urls': ["{0}{1}".format(self._url, div.a.get("href").lstrip('/')) for div in prop_coll.find_all(name='div', class_='Apartment__details')],
                'property_ids': [div.a.get('data-apartment-id') for div in prop_coll.find_all(name='div', class_='Apartment--favorite')]
            }
        elif self.lang=='hun':
            prop_coll=self.parsed_html.find_all(name="div", class_='listing__card')
            page_ids=[(div.a.parent.parent.get("data-id"),
            div.a.parent.parent.get("data-cluster-id"), 
            "{0}{1}".format(self._url, div.a.get("href").lstrip('/'))) for div in prop_coll]
            page={'property_ids':[t[0] for t in page_ids], 'cluster_ids':[t[1] for t in page_ids], 'property_urls':[t[2] for t in page_ids]}   
        return page
    
    def get_property_ids(self):
        page_listings=self.get_page_listings()
        return page_listings.get('property_ids')

    def get_cluster_ids(self):
        ids=self.get_property_ids()
        len_ids=len(ids)
        page_listings=self.get_page_listings()
        return page_listings.get('cluster_ids', [None,]*len_ids)
    
    def get_property_urls(self):
        page_listings=self.get_page_listings()
        return page_listings.get('property_urls')
    
    @staticmethod
    def add_timestamp_to_dict(d, ts_format='%Y-%m-%d %H:%M:%S'):
        now=datetime.datetime.now()
        d['timestamp']=datetime.datetime.strftime(now, ts_format)
        return d
    
    def _create_record(self, url, timestamp=True, **kwargs):
        page_attrs = self.extract_attrs()
        real_estate_params = {'real_estate_hun_page_listings':self}
        real_estate_params['property_url'] = url
        single_property = RealEstateHungary(**real_estate_params)
        if self.photos_dir is not None:
            single_property.extract_photos(self.photos_dir)
        attrs = single_property.extract_attrs()
        attrs.update({**page_attrs, **kwargs})
        if timestamp:
            self.add_timestamp_to_dict(attrs)
        record = pd.DataFrame(attrs, index=[0])
        return record.dropna(axis=1)
    
    def _check_unique_ids(self, in_df, in_df_col_name='property_url'):
        ids=pd.DataFrame(self.get_page_listings())
        if not in_df.empty:
            uniq_urls=~ids.property_urls.isin(in_df[in_df_col_name])
            return ids[uniq_urls]
        else:
            return ids
    
    def listings_to_df(self, num_listings=None, checking_unique_in_df=pd.DataFrame()):
        urls = self.get_property_urls()
        max_listing = len(urls)
        if num_listings and num_listings > max_listing:
            raise ValueError('Given number of listings exceeded the maximum number of listings on the page, please specify equal or less than {0}.'.format(max_listing))
        counter = 0
        records = pd.DataFrame()
        unique_ids = self._check_unique_ids(in_df=checking_unique_in_df)
        for i, r in unique_ids.iterrows():
            prop_id, cluster_id, url=r['property_ids'], r['cluster_ids'], r['property_urls']
            additional_ids = {'property_id':prop_id,
                              'cluster_id':cluster_id}
            single = self._create_record(url, **additional_ids)
            records = pd.concat([records, single], axis=0, sort=False)
            if num_listings:               
                counter += 1
                if counter == num_listings: break
        return records.reset_index(drop=True)
    
class RealEstateHungary:
    '''
    Initialize an object to extract all the available data of the single real estate in Hungary.
    
    Parameters
    ----------
    property_url : string
        URL of the single real estate.
    real_estate_hun_page_listings : RealEstateHungaryPageListings
        Instance of RealEstateHungaryPageListings, which includes information of source real estate page.
    '''
    def __init__(self, property_url, real_estate_hun_page_listings):
        self._real_estate_hun_page_listings=real_estate_hun_page_listings
        self._lang=self._real_estate_hun_page_listings.lang
        self.city=self._real_estate_hun_page_listings.city
        self.src_page_num=self._real_estate_hun_page_listings.page_num
        self.src_listing_type=self._real_estate_hun_page_listings.listing_type
        self.src_property_type=self._real_estate_hun_page_listings.property_type
        self.property_url=remove_spec_chars(property_url)
        try:
            self.parsed_html=RequestWithHeaders(self.property_url).parse_to_html()
        except HTTPError as err:
            if err.code==404:
                raise HTTPError(property_url, err.code, 'Property does not exist, probably already sold/rent or being edited', err.hdrs, err.fp)
        
    def __repr__(self):
        return self.property_url
    
    @property
    def _real_estate_hun_page_listings(self):
        return self._real_estate_hun_page_listings_copy
    
    @_real_estate_hun_page_listings.setter
    def _real_estate_hun_page_listings(self, real_estate_hun_page_listings):
        if not isinstance(real_estate_hun_page_listings, RealEstateHungaryPageListings):
            raise BaseException('Please provide an instance of RealEstateHungaryPageListings class.')       
        self._real_estate_hun_page_listings_copy=real_estate_hun_page_listings
    
    def _inactive_text_exist(self):
        if self._lang=='hun':
            inactive_text=self.parsed_html.find("div", class_="inactive-text").get_text()
        elif self._lang=='eng':
            return None
        return True if inactive_text else False
    
    @property
    def is_active(self):
        is_ad_active=True
        if self._lang=='hun':
            try:
                if self._inactive_text_exist(): is_ad_active=False
            except AttributeError:
                pass
        elif self._lang=='eng':
            return self._inactive_text_exist()
        return is_ad_active
    
    @property
    def gps_coordinates(self):
        if self._lang=='hun':
            gps_img=self.parsed_html.find("a", class_="static-map", href="#terkep").img.get("src")
            lat, lng=gps_img.split("&")[2].split("=")[1].split(",")
            gps_coordinates={'lat': float(lat), 'lng': float(lng)}
        elif self._lang=='eng':
            raw_html=str(self.parsed_html)
            gps_keyword='map.addMarker'
            intermed_part=raw_html[raw_html.find(gps_keyword)+len(gps_keyword):]
            result=re.sub(pattern='[[({})]', string=intermed_part[:intermed_part.find(',title')], repl='')
            try:
                gps_coordinates={v.split(':')[0]: float(v.split(':')[1].strip()) for v in result.split(',')}
            except IndexError:
                gps_coordinates={'lat': None, 'lng': None}
        return gps_coordinates

    @property
    def latitude(self):
        return self.gps_coordinates['lat']
    
    @property
    def longitude(self):
        return self.gps_coordinates['lng']
    
    @property
    def full_address(self):
        if self._lang=='hun':
            addrs_full=self.parsed_html.find("h1", class_="js-listing-title").get_text()
            try:
                city_district, addrs = addrs_full.split(",")
            except ValueError:
                city_district, addrs = addrs_full, None
            full_addrs_d={'city_district': city_district, 'address': None if addrs is None else addrs.strip()}
        elif self._lang=='eng':
            addrs_full=self.parsed_html.find(name='h1', class_='ApartmentPage__Title').get_text()
            city_district = ','.join(addrs_full.split(',')[1:])
            full_addrs_d={'city_district': city_district.strip(), 'address': None}
        return full_addrs_d
    
    @property
    def city_district(self):
        return self.full_address['city_district']
    
    @property
    def address(self):
        return self.full_address['address']
    
    @property
    def main_params(self):
        if self._lang=='hun':
            listing_params=self.parsed_html.find('div', class_='listing-parameters')
            main_params={'_'.join(par.get('class')[1].split('-')[1:]): par.find(name='span', class_='parameter-value').get_text().strip() for par in listing_params.find_all('div')}
            main_params['price']={'huf': main_params['price']}
        elif self._lang=='eng':
            price_huf=self.parsed_html.find(name='h4', class_='ApartmentPage__Price').get_text()
            price_eur=self.parsed_html.find(name='span', class_='ApartmentPage__Price--eur').get_text()
            main_params={'price':{'huf': price_huf.strip(), 'eur': price_eur.strip()}}
        return main_params

    @property
    def price(self):
        return self.main_params.get('price', None)
    
    @property
    def area_size(self):
        if self._lang=='hun':
            return self.main_params.get('area_size')
        elif self._lang=='eng':
            return self.param_details.get('ground_area_size', None)
    
    @property
    def lot_size(self):
        if self._lang=='hun':
            return self.main_params.get('lot_size', None)
        elif self._lang=='eng':
            return self.param_details.get('size_of_land', None)
        
    @property
    def room(self):
        return self.main_params.get('room', None)

    @property
    def param_details(self):
        if self._lang=='hun':
            details_l=[td.string for td in self.parsed_html.find("div", class_="paramterers").find_all("td")]
            details_d={k.replace(" ", "_").lower(): v.replace(",", "|") for k, v in zip(details_l[::2],details_l[1::2])}
        elif self._lang=='eng':
            details_section=self.parsed_html.find(name='div', class_='row ApartmentPage__detailsrow')
            details_cols=details_section.find_all(name='div', class_='col-sm-4')
            all_details_d={col.div.label.get_text(): col.div.p.get_text().strip() for col in details_cols}
            NA_STR='n/a'
            details_d={}
            for k, v in all_details_d.items():
                if v!=NA_STR:
                    details_d.update({k.replace(' ', '_').lower():v})
        return details_d
    
    @property
    def public_transports(self):
        transports={}
        if self._lang=='hun':
            transports_html=self.parsed_html.find("div", class_="public-transports")
            if transports_html:
                for div in transports_html.find_all("div",class_="public-transport-group"):
                    transport_modes_lines={div.span.get_text().lower(): [a.get_text().strip() for a in div.find_all("a")]}
                    transport_modes_lines_cnt= {'{}_count'.format(mode.lower()): len(lines) for mode, lines in transport_modes_lines.items()}
                    transport_modes_lines_cat={mode: "|".join(lines) for mode, lines in transport_modes_lines.items()}
                    transports.update({**transport_modes_lines_cat, **transport_modes_lines_cnt})
        elif self._lang=='eng':
            pass
        return transports

    @property
    def desc(self):
        desc=None
        if self._lang=='hun':
            if self.parsed_html.find('div', class_='long-description'):
                desc_html_tag=self.parsed_html.find('div', class_='long-description')
                desc=desc_html_tag.get_text()
        elif self._lang=='eng':
            desc_html_tag=self.parsed_html.find('div', class_='ApartmentPage__section')
            sections=[' '.join(sect.split()) for sect in [p.get_text() for p in desc_html_tag.find_all(name='p')]]
            desc=' '.join(sections)
        return desc
    
    @property
    def all_attributes(self):
        all_attributes = None
        if self._lang=='hun':
            head= self.parsed_html.find('head')
            script = head.find_all('script')[2].get_text().strip()
            all_attributes = json.loads(script.split('(')[1].split(')')[0])
        return all_attributes
    
    @property
    def _photos(self):
        if self._lang == 'hun':
            card_listing = self.parsed_html.find('div', class_='card listing')
            script = card_listing.script.get_text().strip()
            photos = json.loads(script.split('=')[1].split(';')[0].strip())
            return photos
        elif self._lang == 'eng':
            images = self.parsed_html.find('div', class_ = 'row ApartmentImage__list')
            photos = [image.get('href') for image in images.find_all('a')]
            return photos
    
    @property
    def num_photos(self):
        return len(self._photos)
        
    def extract_photos(self, save_dir):
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        for photo in self._photos:
            if self._lang == 'hun':
                fp = os.path.split(photo['large_url'])[1]
                fn, ext = os.path.splitext(fp)
                save_path = os.path.join(save_dir, '{0}_{1}{2}'.format(fn, photo['label'], ext))
                r = RequestWithHeaders(photo['large_url'])
            elif self._lang == 'eng':
                fn = os.path.split(photo)[1]
                ext = '.jpg'
                save_path = os.path.join(save_dir, '{0}{2}'.format(fn, ext))
                r = RequestWithHeaders(photo)
            r.download(save_path)
            
    def _extract_single_attrs_to_dict(self):
        single_attrs={'property_url': self.property_url,
        'city_district': self.city_district,
        'address': self.address,
        'lot_size': self.lot_size,
        'area_size': self.area_size,
        'room': self.room,
        'photos': self.num_photos,
        'desc': self.desc}
        return single_attrs
    
    def _extract_multiple_attrs_to_dict(self):
        price_in_diff_currency={'price_in_{}'.format(k):v for k, v in self.price.items()}
        multiple_attrs={**price_in_diff_currency,
                        **self.gps_coordinates,
                        **self.param_details,
                        **self.public_transports}
        return multiple_attrs
    
    def extract_attrs(self):
        single=self._extract_single_attrs_to_dict()
        multiple=self._extract_multiple_attrs_to_dict()
        union={**single, **multiple}
        return union
    
    def attrs_to_df(self):
        record=pd.DataFrame(self.extract_attrs())
        return record.dropna(axis=1)
