import streamlit as st
import requests
import xml.etree.ElementTree as ET

# Title
st.title("PubMed Article Search")

# Search term input
search_term = st.text_input("Enter a search term:")

# Page number input
page = st.number_input("Page", min_value=1, value=1, step=1)

# Search PubMed API
if st.button("Search"):
    if search_term:
        base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
        url = f'{base_url}?db=pubmed&term={search_term}&retmode=json&retstart={((page - 1) * 10)}&retmax=10'
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            pubmed_ids = data['esearchresult']['idlist']
            total_results = int(data['esearchresult']['count'])
            total_pages = (total_results // 10) + 1
            
            for pubmed_id in pubmed_ids:
                summary_url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pubmed_id}&retmode=json'
                summary_response = requests.get(summary_url)
                summary_response.raise_for_status()
                
                summary_data = summary_response.json()
                article_title = summary_data['result'][pubmed_id]['title']
                article_url = f'https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/'
                
                st.write(f"### [{article_title}]({article_url})")
                
                authors = summary_data['result'][pubmed_id]['authors']
                author_names = ", ".join([author['name'] for author in authors])
                
                st.write(f"**Authors:** {author_names}")

                # Abstract fetching logic
                base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
                abstract_url = f'{base_url}?db=pubmed&id={pubmed_id}&retmode=xml'
                response = requests.get(abstract_url)
                xml_data = response.text
                root = ET.fromstring(xml_data)
                
                abstract_elements = root.findall('.//AbstractText')
                
                abstract_text = '\n'.join(e.text.strip() for e in abstract_elements if e.text)
                st.write(f"**Abstract:** {abstract_text}")

        except requests.exceptions.RequestException as e:
            st.write(f"An error occurred: {str(e)}")
