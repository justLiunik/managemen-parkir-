import mysql.connector
from mysql.connector import Error
from datetime import datetime
from config import DB_CONFIG, IMAGES_DIR
import os

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish connection to MySQL database"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                print("✓ Connected to MySQL database successfully")
        except Error as e:
            print(f"✗ Error connecting to MySQL: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✓ Disconnected from MySQL database")
    
    def add_incoming_vehicle(self, number, license_plate, vehicle_type, image_path=None):
        """Add a new incoming vehicle to the database"""
        try:
            cursor = self.connection.cursor()
            time_of_entry = datetime.now()
            
            # Read image file if provided
            image_data = None
            image_filename = None
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as img_file:
                    image_data = img_file.read()
                image_filename = os.path.basename(image_path)
            
            query = """
            INSERT INTO vehicles (number, license_plate, vehicle_type, time_of_entry, image_filename, status)
            VALUES (%s, %s, %s, %s, %s, 'parked')
            """
            
            if image_data:
                query = """
                INSERT INTO vehicles (number, license_plate, vehicle_type, time_of_entry, vehicle_image, image_filename, status)
                VALUES (%s, %s, %s, %s, %s, %s, 'parked')
                """
                cursor.execute(query, (number, license_plate, vehicle_type, time_of_entry, image_data, image_filename))
            else:
                cursor.execute(query, (number, license_plate, vehicle_type, time_of_entry, image_filename))
            
            self.connection.commit()
            print(f"✓ Vehicle {license_plate} added successfully (Entry time: {time_of_entry})")
            return True
        except Error as e:
            print(f"✗ Error adding vehicle: {e}")
            return False
    
    def record_outgoing_vehicle(self, license_plate):
        """Record the exit time of a vehicle"""
        try:
            cursor = self.connection.cursor()
            time_of_exit = datetime.now()
            
            # Get vehicle entry time first
            cursor.execute(
                "SELECT time_of_entry, id FROM vehicles WHERE license_plate = %s AND status = 'parked'",
                (license_plate,)
            )
            result = cursor.fetchone()
            
            if not result:
                print(f"✗ Vehicle with license plate {license_plate} not found or already exited")
                return False
            
            time_of_entry, vehicle_id = result
            duration = int((time_of_exit - time_of_entry).total_seconds() / 60)  # Duration in minutes
            
            query = """
            UPDATE vehicles 
            SET time_of_exit = %s, duration = %s, status = 'exited'
            WHERE id = %s
            """
            cursor.execute(query, (time_of_exit, duration, vehicle_id))
            self.connection.commit()
            
            hours = duration // 60
            minutes = duration % 60
            print(f"✓ Vehicle {license_plate} exited successfully")
            print(f"  Entry: {time_of_entry}")
            print(f"  Exit: {time_of_exit}")
            print(f"  Duration: {hours}h {minutes}m")
            return True
        except Error as e:
            print(f"✗ Error recording outgoing vehicle: {e}")
            return False
    
    def get_all_vehicles(self):
        """Get list of all vehicles"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
            SELECT id, number, license_plate, vehicle_type, time_of_entry, 
                   time_of_exit, duration, status
            FROM vehicles
            ORDER BY id DESC
            """
            cursor.execute(query)
            vehicles = cursor.fetchall()
            return vehicles
        except Error as e:
            print(f"✗ Error retrieving vehicles: {e}")
            return []
    
    def get_parked_vehicles(self):
        """Get list of currently parked vehicles"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
            SELECT id, number, license_plate, vehicle_type, time_of_entry, status
            FROM vehicles
            WHERE status = 'parked'
            ORDER BY time_of_entry DESC
            """
            cursor.execute(query)
            vehicles = cursor.fetchall()
            return vehicles
        except Error as e:
            print(f"✗ Error retrieving parked vehicles: {e}")
            return []
    
    def get_vehicle_by_license_plate(self, license_plate):
        """Get vehicle details by license plate"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
            SELECT * FROM vehicles 
            WHERE license_plate = %s
            """
            cursor.execute(query, (license_plate,))
            vehicle = cursor.fetchone()
            return vehicle
        except Error as e:
            print(f"✗ Error retrieving vehicle: {e}")
            return None
    
    def delete_vehicle(self, vehicle_id):
        """Delete a vehicle record"""
        try:
            cursor = self.connection.cursor()
            query = "DELETE FROM vehicles WHERE id = %s"
            cursor.execute(query, (vehicle_id,))
            self.connection.commit()
            
            if cursor.rowcount > 0:
                print(f"✓ Vehicle deleted successfully")
                return True
            else:
                print(f"✗ Vehicle not found")
                return False
        except Error as e:
            print(f"✗ Error deleting vehicle: {e}")
            return False
    
    def get_parking_statistics(self):
        """Get parking lot statistics"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Total parked vehicles
            cursor.execute("SELECT COUNT(*) as count FROM vehicles WHERE status = 'parked'")
            parked_count = cursor.fetchone()['count']
            
            # Total vehicles (all time)
            cursor.execute("SELECT COUNT(*) as count FROM vehicles")
            total_count = cursor.fetchone()['count']
            
            # Vehicles exited today
            cursor.execute("""
                SELECT COUNT(*) as count FROM vehicles 
                WHERE status = 'exited' AND DATE(time_of_exit) = CURDATE()
            """)
            exited_today = cursor.fetchone()['count']
            
            # Average parking duration
            cursor.execute("""
                SELECT AVG(duration) as avg_duration FROM vehicles 
                WHERE duration IS NOT NULL
            """)
            avg_duration = cursor.fetchone()['avg_duration']
            
            return {
                'parked_vehicles': parked_count,
                'total_vehicles': total_count,
                'exited_today': exited_today,
                'avg_duration_minutes': int(avg_duration) if avg_duration else 0
            }
        except Error as e:
            print(f"✗ Error retrieving statistics: {e}")
            return {}
