from fastapi import FastAPI
from fastapi.responses import FileResponse
import requests

app = FastAPI()

@app.get("/")
def index():
    return FileResponse("index.html")

@app.get("/manifest.json")
def manifest():
    return FileResponse("manifest.json")

@app.get("/sw.js")
def service_worker():
    return FileResponse("sw.js")

@app.get("/search")
def search(address: str):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "jsonv2",
        "limit": 1
    }
    headers = {
        "User-Agent": "GasStationSearchApp/1.0"
    }
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    if len(data) == 0:
        return {"message": "住所が見つかりませんでした"}
    latitude = data[0]["lat"]
    longitude = data[0]["lon"]
    # NAVITIME APIが利用でき次第実装する
    navitime_url = "https://{HOST}/{CID}/v1/gas_station"
    navitime_params = {
        "coord": latitude + "," + longitude,
        "radius": 3000,
        "options": "detail",
        "limit": 10
    }
    navitime_headers = {
        "Authorization": "Bearer APIキー"
    }
    response = requests.get(
        navitime_url,
        params=navitime_params,
        headers=navitime_headers
    )
    if response.status_code != 200:
        return {
            "message": "NAVITIME APIからデータを取得できませんでした",
            "status_code": response.status_code
        }
    navitime_data = response.json()
    results = []
    for station in navitime_data.get("items", []):
        name = station.get("name", "名称不明")
        distance = station.get("distance")
        details = station.get("details", {})
        fuel_price = details.get("fuel_price", {})
        regular = fuel_price.get("regular")
        high_octane = fuel_price.get("high_octane")
        diesel = fuel_price.get("diesel")
        results.append({
            "name": name,
            "distance": distance,
            "regular": regular,
            "high_octane": high_octane,
            "diesel": diesel
        })

    return results
