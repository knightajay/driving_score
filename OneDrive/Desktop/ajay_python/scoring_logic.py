import pandas as pd
import numpy as np

def process_and_score(sensor_path, driving_path):
    # Load Data
    sensor_df = pd.read_csv(sensor_path)
    driving_df = pd.read_csv(driving_path)

    # Merge data on frame_number
    # We bring in GPS coordinates, Speed, and Acceleration data
    merged_df = pd.merge(
        driving_df, 
        sensor_df[['frame_number', 'Latitude', 'Longitude', 'gps_speed_kmh', 'imu_accel_magnitude']], 
        on='frame_number', 
        how='left'
    )

    # Fill NaNs in numeric columns to avoid math errors
    merged_df['gps_speed_kmh'] = merged_df['gps_speed_kmh'].fillna(0)
    merged_df['distance_m'] = merged_df['distance_m'].fillna(100) # Assume clear road if no distance
    merged_df['imu_accel_magnitude'] = merged_df['imu_accel_magnitude'].fillna(9.8)

    base_score = 100.0
    
    # 1. Speeding Penalty: Deduct 0.1 per frame over 60 km/h
    speeding_frames = merged_df[merged_df['gps_speed_kmh'] > 60]['frame_number'].nunique()
    speeding_penalty = speeding_frames * 0.1

    # 2. Tailgating Penalty: Fast speed (>20) + Close distance (<15m)
    # Filter for vehicles only (car, truck, motorcycle)
    vehicles = merged_df[merged_df['class'].isin(['car', 'truck', 'motorcycle'])]
    tailgate_frames = vehicles[(vehicles['gps_speed_kmh'] > 20) & (vehicles['distance_m'] < 15)]['frame_number'].nunique()
    tailgate_penalty = tailgate_frames * 0.5

    # 3. Harsh Driving: High IMU G-force (Threshold > 13.0 m/s^2)
    harsh_frames = merged_df[merged_df['imu_accel_magnitude'] > 13.0]['frame_number'].nunique()
    harsh_penalty = harsh_frames * 2.0

    # Final Calculation
    final_score = max(0, base_score - (speeding_penalty + tailgate_penalty + harsh_penalty))

    return {
        "score": round(final_score, 1),
        "breakdown": {
            "speeding": round(speeding_penalty, 1),
            "tailgating": round(tailgate_penalty, 1),
            "harsh_maneuvers": round(harsh_penalty, 1)
        },
        "trip_summary": {
            "max_speed": round(merged_df['gps_speed_kmh'].max(), 1),
            "total_frames": int(merged_df['frame_number'].max())
        }
    }