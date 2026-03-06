#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Places API Verifier for Katalog-AI
Функция: Проверка через Google Places API
Вход: название и адрес бизнеса
Выход: place_id, рейтинг, количество отзывов, координаты

Документация: https://developers.google.com/maps/documentation/places/web-service/overview
"""

import requests
import json
import os
from typing import Dict, Optional, List
from datetime import datetime

class GooglePlacesVerifier:
    """Класс для верификации бизнесов через Google Places API"""
    
    BASE_URL = "https://maps.googleapis.com/maps/api"
    
    def __init__(self, api_key: str):
        """
        Инициализация верификатора
        
        Args:
            api_key: API ключ Google Places (из GitHub Secrets)
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Katalog-AI-Verifier/1.0"
        })
    
    def search_text(self, query: str, location: str = "Almaty, Kazakhstan") -> Optional[Dict]:
        """
        Текстовый поиск плана по названию и адресу
        
        Args:
            query: Название или адрес бизнеса
            location: Город/страна для ограничения поиска
            
        Returns:
            Первый найденный результат
        """
        try:
            params = {
                "query": f"{query} {location}",
                "key": self.api_key
            }
            
            response = self.session.get(
                f"{self.BASE_URL}/place/textsearch/json",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("results"):
                return data["results"][0]
            
            return None
            
        except requests.RequestException as e:
            print(f"❌ Ошибка при поиске в Google Places: {e}")
            return None
    
    def get_place_details(self, place_id: str, fields: List[str] = None) -> Optional[Dict]:
        """
        Получить подробную информацию о месте
        
        Args:
            place_id: ID места в Google Places
            fields: Список полей для получения
            
        Returns:
            Детали места
        """
        try:
            if fields is None:
                fields = [
                    "name",
                    "rating",
                    "review_count",
                    "formatted_address",
                    "geometry",
                    "formatted_phone_number",
                    "website",
                    "opening_hours",
                    "business_status",
                    "types"
                ]
            
            params = {
                "place_id": place_id,
                "fields": ",".join(fields),
                "key": self.api_key
            }
            
            response = self.session.get(
                f"{self.BASE_URL}/place/details/json",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("result"):
                return data["result"]
            
            return None
            
        except requests.RequestException as e:
            print(f"❌ Ошибка при получении деталей места: {e}")
            return None
    
    def verify_business(self, business_name: str, address: str, city: str = "Алматы") -> Dict:
        """
        Полная верификация бизнеса через Google Places
        
        Args:
            business_name: Название бизнеса
            address: Адрес бизнеса
            city: Город
            
        Returns:
            Словарь с результатами верификации
        """
        result = {
            "verified": False,
            "source": "google_places",
            "business_name": business_name,
            "address": address,
            "city": city,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": None,
            "error": None
        }
        
        try:
            # Шаг 1: Текстовый поиск
            print(f"🔍 Поиск '{business_name}' в Google Places...")
            search_query = f"{business_name} {address} {city}"
            place = self.search_text(search_query)
            
            if not place:
                result["error"] = f"Место не найдено в Google Places"
                print(f"⚠️ {result['error']}")
                return result
            
            # Шаг 2: Получение полной информации
            place_id = place.get("place_id")
            print(f"✅ Найдено: {place.get('name')} (Place ID: {place_id})")
            
            place_details = self.get_place_details(place_id)
            
            if place_details:
                result["verified"] = True
                
                geometry = place_details.get("geometry", {})
                location = geometry.get("location", {})
                
                result["data"] = {
                    "place_id": place_id,
                    "name": place_details.get("name"),
                    "address": place_details.get("formatted_address"),
                    "phone": place_details.get("formatted_phone_number"),
                    "website": place_details.get("website"),
                    "rating": place_details.get("rating"),
                    "review_count": place_details.get("user_ratings_total"),
                    "business_status": place_details.get("business_status"),
                    "geo": {
                        "latitude": location.get("lat"),
                        "longitude": location.get("lng")
                    },
                    "google_maps_url": f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                    "types": place_details.get("types", [])
                }
                
                rating = place_details.get("rating", "N/A")
                review_count = place_details.get("user_ratings_total", 0)
                print(f"✅ Верифицировано! Рейтинг: {rating}/5 ({review_count} отзывов)")
        
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ Ошибка: {e}")
        
        return result


def main():
    """Основная функция для тестирования"""
    
    # Получаем API ключ из переменной окружения
    api_key = os.getenv("GOOGLE_PLACES_API_KEY", "demo-key")
    
    if api_key == "demo-key":
        print("⚠️ ВАЖНО: Установите переменную окружения GOOGLE_PLACES_API_KEY")
        print("Получить ключ: https://developers.google.com/maps/documentation/places/")
        return
    
    # Инициализируем верификатор
    verifier = GooglePlacesVerifier(api_key)
    
    # Примеры бизнесов для проверки
    businesses = [
        {
            "name": "Beauty Prime Salon",
            "address": "ул. Жибек Жолы, 50",
            "city": "Алматы"
        },
        {
            "name": "Glow Up Clinic",
            "address": "ул. Аль-Фараби, 77",
            "city": "Алматы"
        },
        {
            "name": "National Museum",
            "address": "ул. Парк-культуры, 4",
            "city": "Нур-Султан"
        }
    ]
    
    results = []
    
    print("=" * 60)
    print("🚀 Запуск Google Places верификации")
    print("=" * 60)
    
    for business in businesses:
        print(f"\n📍 Проверка: {business['name']} ({business['city']})")
        verification = verifier.verify_business(
            business["name"],
            business["address"],
            business["city"]
        )
        results.append(verification)
    
    # Сохраняем результаты
    output_file = "verification_results_google.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Результаты сохранены в {output_file}")
    print(f"✅ Успешно верифицировано: {sum(1 for r in results if r['verified'])}/{len(results)}")


if __name__ == "__main__":
    main()
