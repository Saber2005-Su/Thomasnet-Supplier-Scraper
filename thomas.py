from playwright.sync_api import sync_playwright
import csv
import time

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-features=IsolateOrigins,site-per-process',
            '--no-sandbox',
            '--disable-dev-shm-usage'
        ]
    )
    
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        viewport={'width': 1920, 'height': 1080}
    )
    
    page = context.new_page()
    
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)
    
    # লিস্ট পেজে যাও
    page.goto("https://www.thomasnet.com/suppliers/usa/special-custom-designers-builders-manufacturers-machinery-48630404")
    page.wait_for_timeout(15000)
    
    # সব কার্ডের তথ্য প্রথমে সংগ্রহ করো
    cards_info = []
    cards = page.query_selector_all('li.search-result-supplier_searchResultSupplierPanel__HdR9H')
    print(f"মোট {len(cards)} টি কার্ড পাওয়া গেছে\n")
    
    for card in cards:
        # কোম্পানির নাম
        name_elem = card.query_selector('button[data-testid="supplier-name-link"]')
        name = name_elem.inner_text() if name_elem else "N/A"
        
        # লোকেশন
        location_elem = card.query_selector('a[data-testid="srp.supplier-location-link"] span')
        location = location_elem.inner_text() if location_elem else "N/A"
        
        # প্রোফাইল লিংক
        profile_elem = card.query_selector('a:has-text("View Profile")')
        profile_url = profile_elem.get_attribute('href') if profile_elem else "N/A"
        if profile_url and profile_url.startswith('/'):
            profile_url = f"https://www.thomasnet.com{profile_url}"
        
        # ওয়েবসাইট লিংক
        website_elem = card.query_selector('a.supplier-card-header_visitWebsiteButton__YRLNP')
        website_url = website_elem.get_attribute('href') if website_elem else "N/A"
        
        cards_info.append({
            'name': name,
            'location': location,
            'profile_url': profile_url,
            'website_url': website_url
        })
    
    print(f"✅ {len(cards_info)} টি কোম্পানির বেসিক তথ্য সংগ্রহ完毕\n")
    
    # এখন আলাদাভাবে প্রতিটি প্রোফাইল পেজে গিয়ে ফোন নম্বর সংগ্রহ
    all_data = []
    
    for i, info in enumerate(cards_info, 1):
        print(f"[{i}] প্রসেসিং: {info['name']}")
        
        phone_number = "N/A"
        
        if info['profile_url'] != "N/A":
            try:
                # নতুন পেজ তৈরি করো (যাতে লিস্ট পেজ নষ্ট না হয়)
                profile_page = context.new_page()
                profile_page.goto(info['profile_url'], wait_until='networkidle')
                profile_page.wait_for_timeout(3000)
                
                # View Phone Number বাটনে ক্লিক
                view_phone_button = profile_page.query_selector('button.supplier-info_desktopViewPhoneButton__YswWj')
                
                if view_phone_button:
                    view_phone_button.click()
                    profile_page.wait_for_timeout(2000)
                    
                    # ডায়ালগ থেকে ফোন নম্বর নাও
                    dialog = profile_page.query_selector('dialog[open]')
                    if dialog:
                        phone_link = dialog.query_selector('a[href^="tel:"]')
                        if phone_link:
                            phone_number = phone_link.inner_text().strip()
                            print(f"   📞 ফোন: {phone_number}")
                        else:
                            print(f"   ⚠️ ফোন লিংক পাওয়া যায়নি")
                        
                        # ডায়ালগ বন্ধ করো
                        close_btn = dialog.query_selector('button[slot="close"]')
                        if close_btn:
                            close_btn.click()
                    else:
                        print(f"   ⚠️ ডায়ালগ পাওয়া যায়নি")
                else:
                    print(f"   ⚠️ View Phone Number বাটন নেই")
                
                profile_page.close()  # পেজটা বন্ধ করে দাও
                
            except Exception as e:
                print(f"   ❌ এরর: {str(e)[:80]}")
        
        all_data.append({
            'name': info['name'],
            'location': info['location'],
            'phone': phone_number,
            'website_url': info['website_url'],
            'profile_url': info['profile_url']
        })
        
        print(f"   📍 {info['location']}")
        print("-" * 50)
        time.sleep(1)  # একটু বিরতি
    
    # CSV ফাইল সেভ
    csv_filename = 'thomasnet_suppliers_with_phone.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['name', 'location', 'phone', 'website_url', 'profile_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_data)
    
    print(f"\n✅ মোট {len(all_data)} টি কোম্পানির ডাটা সংগ্রহ হয়েছে!")
    print(f"📁 CSV ফাইল সেভ হয়েছে: {csv_filename}")
    
    browser.close()