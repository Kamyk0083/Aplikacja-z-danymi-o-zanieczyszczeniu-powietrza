from flask import Flask, request, jsonify
from flask.views import MethodView
from datetime import datetime
from typing import Optional, List
import pydantic

app = Flask(__name__)

class DataStorage:
    def __init__(self):
        self.records: List[WeatherAndAirQualityData] = []

    def add_record(self, record):
        self.records.append(record)

    def find_closest_record(self, timestamp):
        try:
            return min(
                self.records,
                key=lambda x: abs(x.timestamp - timestamp),
                default=None
            )
        except ValueError:
            return None

storage = DataStorage()

class WeatherAndAirQualityData(pydantic.BaseModel):
    timestamp: datetime
    temperature: Optional[int] = pydantic.Field(None, ge=-50, le=50)
    pressure: Optional[int] = pydantic.Field(None, ge=800, le=1200)
    humidity: Optional[int] = pydantic.Field(None, ge=0, le=100)
    aqi: Optional[int] = pydantic.Field(None, ge=0)

class AirQualityRecordView(MethodView):
    def get(self):
        timestamp_query = request.args.get('timestamp')
        if not timestamp_query:
            return jsonify({"error": "Timestamp query parameter is required."}), 400

        query_timestamp = datetime.fromisoformat(timestamp_query)
        closest_record = storage.find_closest_record(query_timestamp)
        return jsonify(closest_record.dict()) if closest_record else jsonify({"message": "No data found."}), 404
        
    def post(self):
        data = request.json
        try:
            record = WeatherAndAirQualityData(**data)
            storage.add_record(record)
            return jsonify(record.dict()), 201
        except pydantic.ValidationError as e:
            return jsonify({"error": str(e)}), 400

app.add_url_rule('/air_quality', view_func=AirQualityRecordView.as_view('air_quality_api'))

if __name__ == '__main__':
    app.run(debug=True)
