import requests
from bs4 import BeautifulSoup
import json
import time

def parse_rust_tm():
    base_url = "https://rust.tm/"
    all_skins = []
    seen_links = set() # Здесь будем хранить ссылки, чтобы проверять на дубликаты
    page = 1
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }

    print("🚀🚀 Погнали собирать скины...")

    while True:
        url = f"{base_url}?t=all&p={page}&sd=desc"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Ищем блок, где лежат именно товары, чтобы не цеплять лишнее из меню
            items_container = soup.find('div', id='applications')
            if not items_container:
                print("Контейнер с товарами не найден. Выходим.")
                break

            items = items_container.find_all('a', class_='item')

            # Проверка 1: Если на странице физически нет карточек
            if not items:
                print(f"На странице {page} пусто. Красиво уходим.")
                break

            new_items_on_this_page = 0

            for item in items:
                link = item.get('href')
                if not link: continue
                
                full_link = f"https://rust.tm{link}"
                
                # Проверка 2: Если мы уже видели эту ссылку раньше — это дубликат
                if full_link in seen_links:
                    continue
                
                seen_links.add(full_link)
                new_items_on_this_page += 1

                name_tag = item.find('div', class_='name')
                price_tag = item.find('div', class_='price')

                all_skins.append({
                    "name": name_tag.get_text(strip=True) if name_tag else "N/A",
                    "price": price_tag.get_text(strip=True).replace('\xa0', ' ') if price_tag else "0",
                    "link": full_link
                })

            # Если на всей странице не нашлось НИ ОДНОГО нового скина — значит, пошел повтор
            if new_items_on_this_page == 0:
                print(f"Страница {page} не дала новых скинов. Видимо, это конец.")
                break

            print(f"✅ Страница {page} готова (собрано: {len(all_skins)})")
            page += 1
            time.sleep(1) # Не злим сервер

        except Exception as e:
            print(f"Ошибка на странице {page}: {e}")
            break

    # Сохраняем результат
    with open('rust_skins_full.json', 'w', encoding='utf-8') as f:
        json.dump(all_skins, f, indent=4, ensure_ascii=False)
    
    print(f"\n🎉 Финиш! Собрано скинов: {len(all_skins)}")

if __name__ == "__main__":
    parse_rust_tm()
