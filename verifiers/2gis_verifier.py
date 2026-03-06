#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2GIS API Verifier for Katalog-AI
Функция: Проверка бизнеса через 2ГИС API
Вход: URL или ID организации в 2ГИС
Выход: верифицированные данные (название, адрес, координаты, рубрика)

Документация API: https://docs.2gis.com/ru/api
"""

import requests
import json
import os
from typing import Dict, Optional, List
from datetime import datetime

class TwoGISVerifier:
    """Класс для верификации бизнесов через 2ГИС API"""
    
    BASE_URL = "https://api.2gis.com/3.0"
    
    def __init__(self, api_key: str):
        """
        Инициализация верификатора
        
        Args:
            api_key: API ключ от 2ГИС (из GitHub Secrets)
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Katalog-AI-Verifier/1.0"
        })
    
    def search_business(self, name: str, city: str = "Алматы") -> Optional[Dict]:
        """
        Поиск бизнеса по названию и городу
        
        Args:
            name: Название бизнеса
            city: Город поиска
            
        Returns:
            Первый найденный результат с данными бизнеса
        """
        try:
            params = {
                "q": f"{name} {city}",
                "key": self.api_key,
                "limit": 1
            }
            
            response = self.session.get(
                f"{self.BASE_URL}/search/",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("result", {}).get("items"):
                return data["result"]["items"][0]
            
            return None
            
        except requests.RequestException as e:
            print(f"❌ Ошибка при поиске в 2ГИС: {e}")
            return None
    
    def get_firm_details(self, firm_id: str) -> Optional[Dict]:
        """
        Получить полную информацию об организации по ID
        
        Args:
            firm_id: ID организации в 2ГИС
            
        Returns:
            Полные данные организации
        """
        try:
            params = {
                "id": firm_id,
                "key": self.api_key
            }
            
            response = self.session.get(
                f"{self.BASE_URL}/org/",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("result"):
                return data["result"]
            
            return None
            
        except requests.RequestException as e:
            print(f"❌ Ошибка при получении деталей организации: {e}")
            return None
    
    def verify_business(self, business_name: str, business_city: str) -> Dict:
        """
        Полная верификация бизнеса через 2ГИС
        
        Args:
            business_name: Название бизнеса
            business_city: Город, где находится бизнес
            
        Returns:
            Словарь с результатами верификации
        """
        result = {
            "verified": False,
            "source": "2gis",
            "business_name": business_name,
            "city": business_city,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": None,
            "error": None
        }
        
        try:
            # Шаг 1: Поиск бизнеса
            print(f"🔍 Поиск '{business_name}' на 2ГИС...")
            firm = self.search_business(business_name, business_city)
            
            if not firm:
                result["error"] = f"Бизнес '{business_name}' не найден на 2ГИС"
                print(f"⚠️ {result['error']}")
                return result
            
            # Шаг 2: Получение полной информации
            firm_id = firm.get("id")
            print(f"✅ Найден: {firm.get('name')} (ID: {firm_id})")
            
            firm_details = self.get_firm_details(firm_id)
            
            if firm_details:
                result["verified"] = True
                result["data"] = {
                    "2gis_id": firm_id,
                    "name": firm_details.get("name"),
                    "address": firm_details.get("address_name"),
                    "phone": firm_details.get("phone"),
                    "website": firm_details.get("website"),
                    "rate": firm_details.get("rate"),
                    "review_count": firm_details.get("review_count"),
                    "geo": {
                        "latitude": firm_details.get("geo", {}).get("lat"),
                        "longitude": firm_details.get("geo", {}).get("lon")
                    },
                    "type": firm_details.get("type"),
                    "2gis_url": f"https://2gis.kz/almaty/firm/{firm_id}"
                }
                print(f"✅ Верифицировано! Рейтинг: {firm_details.get('rate')}/5")
        
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ Ошибка: {e}")
        
        return result


def main():
    """Основная функция для тестирования"""
    
    # Получаем API ключ из переменной окружения (GitHub Secret)
    api_key = os.getenv("TWOGIS_API_KEY", "demo-key")
    
    if api_key == "demo-key":
        print("⚠️ ВАЖНО: Установите переменную окружения TWOGIS_API_KEY")
        print("Получить ключ: https://api.2gis.com/doc/")
        return
    
    # Инициализируем верификатор
    verifier = TwoGISVerifier(api_key)
    
    # Примеры проверяемых бизнесов из beauty.json
    businesses = [
        {"name": "Beauty Prime Salon", "city": "Алматы"},
        {"name": "Glow Up Clinic", "city": "Алматы"},
        {"name": "Barbershop Gentleman", "city": "Нур-Султан"}
    ]
    
    results = []
    
    print("=" * 60)
    print("🚀 Запуск 2ГИС верификации")
    print("=" * 60)
    
    for business in businesses:
        print(f"\n📍 Проверка: {business['name']} ({business['city']})")
        verification = verifier.verify_business(business["name"], business["city"])
        results.append(verification)
    
    # Сохраняем результаты
    output_file = "verification_results_2gis.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Результаты сохранены в {output_file}")
    print(f"✅ Успешно верифицировано: {sum(1 for r in results if r['verified'])}/{len(results)}")


if __name__ == "__main__":
    main()
