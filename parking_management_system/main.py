import sys
import os
from datetime import datetime
from db_manager import DatabaseManager

class ParkingManagementSystem:
    def __init__(self):
        self.db = DatabaseManager()
    
    def display_menu(self):
        """Display main menu"""
        print("\n" + "="*50)
        print("   PARKING MANAGEMENT SYSTEM")
        print("="*50)
        print("1. Record Incoming Vehicle")
        print("2. Record Outgoing Vehicle")
        print("3. View Vehicle List")
        print("4. View Parking Statistics")
        print("5. Search Vehicle")
        print("6. Delete Vehicle Record")
        print("0. Exit")
        print("="*50)
    
    def record_incoming_vehicle(self):
        """Record a new incoming vehicle"""
        print("\n--- Record Incoming Vehicle ---")
        try:
            number = int(input("Enter vehicle number/ID: "))
            license_plate = input("Enter license plate: ").upper()
            vehicle_type = input("Enter vehicle type (Car/Truck/Motorcycle/Bus): ")
            image_path = input("Enter vehicle image path (or press Enter to skip): ").strip()
            
            # Validate image path
            if image_path and not os.path.exists(image_path):
                print("✗ Image file not found")
                image_path = None
            
            self.db.add_incoming_vehicle(number, license_plate, vehicle_type, image_path if image_path else None)
        except ValueError:
            print("✗ Invalid input. Please enter valid data.")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def record_outgoing_vehicle(self):
        """Record outgoing vehicle"""
        print("\n--- Record Outgoing Vehicle ---")
        print("\nCurrently Parked Vehicles:")
        parked = self.db.get_parked_vehicles()
        
        if not parked:
            print("✗ No vehicles currently parked")
            return
        
        self.display_vehicle_table(parked)
        
        license_plate = input("\nEnter license plate of exiting vehicle: ").upper()
        self.db.record_outgoing_vehicle(license_plate)
    
    def view_vehicle_list(self):
        """Display all vehicles"""
        print("\n--- Vehicle List ---")
        vehicles = self.db.get_all_vehicles()
        
        if not vehicles:
            print("✗ No vehicles in database")
            return
        
        self.display_vehicle_table(vehicles)
    
    def display_vehicle_table(self, vehicles):
        """Display vehicles in a formatted table"""
        print("\n{:<5} {:<12} {:<20} {:<15} {:<20} {:<20} {:<10}".format(
            "ID", "Number", "License Plate", "Type", "Entry Time", "Exit Time", "Status"
        ))
        print("-" * 110)
        
        for vehicle in vehicles:
            vehicle_id = vehicle.get('id', '')
            number = vehicle.get('number', '')
            license = vehicle.get('license_plate', '')
            v_type = vehicle.get('vehicle_type', '')
            entry = vehicle.get('time_of_entry', '')
            exit_time = vehicle.get('time_of_exit', 'N/A')
            status = vehicle.get('status', 'N/A')
            
            # Format times
            if isinstance(entry, datetime):
                entry = entry.strftime("%Y-%m-%d %H:%M:%S")
            if isinstance(exit_time, datetime):
                exit_time = exit_time.strftime("%Y-%m-%d %H:%M:%S")
            
            print("{:<5} {:<12} {:<20} {:<15} {:<20} {:<20} {:<10}".format(
                vehicle_id, number, license, v_type, entry, exit_time, status
            ))
    
    def search_vehicle(self):
        """Search for a specific vehicle"""
        print("\n--- Search Vehicle ---")
        license_plate = input("Enter license plate to search: ").upper()
        
        vehicle = self.db.get_vehicle_by_license_plate(license_plate)
        
        if vehicle:
            print("\n✓ Vehicle Found:")
            print(f"  ID: {vehicle['id']}")
            print(f"  Number: {vehicle['number']}")
            print(f"  License Plate: {vehicle['license_plate']}")
            print(f"  Vehicle Type: {vehicle['vehicle_type']}")
            print(f"  Entry Time: {vehicle['time_of_entry']}")
            print(f"  Exit Time: {vehicle.get('time_of_exit', 'Still Parked')}")
            print(f"  Duration: {vehicle.get('duration', 'N/A')} minutes")
            print(f"  Status: {vehicle['status']}")
        else:
            print(f"✗ Vehicle with license plate '{license_plate}' not found")
    
    def view_statistics(self):
        """Display parking statistics"""
        print("\n--- Parking Statistics ---")
        stats = self.db.get_parking_statistics()
        
        if stats:
            print(f"Currently Parked Vehicles: {stats['parked_vehicles']}")
            print(f"Total Vehicles (All Time): {stats['total_vehicles']}")
            print(f"Vehicles Exited Today: {stats['exited_today']}")
            
            if stats['avg_duration_minutes'] > 0:
                hours = stats['avg_duration_minutes'] // 60
                minutes = stats['avg_duration_minutes'] % 60
                print(f"Average Parking Duration: {hours}h {minutes}m")
            else:
                print("Average Parking Duration: No data available")
    
    def delete_vehicle(self):
        """Delete a vehicle record"""
        print("\n--- Delete Vehicle Record ---")
        try:
            vehicle_id = int(input("Enter vehicle ID to delete: "))
            confirm = input("Are you sure? (yes/no): ").lower()
            
            if confirm == 'yes':
                self.db.delete_vehicle(vehicle_id)
            else:
                print("✗ Deletion cancelled")
        except ValueError:
            print("✗ Invalid vehicle ID")
    
    def run(self):
        """Run the main application loop"""
        print("\n✓ Parking Management System Started")
        
        while True:
            self.display_menu()
            choice = input("Enter your choice (0-6): ").strip()
            
            if choice == '1':
                self.record_incoming_vehicle()
            elif choice == '2':
                self.record_outgoing_vehicle()
            elif choice == '3':
                self.view_vehicle_list()
            elif choice == '4':
                self.view_statistics()
            elif choice == '5':
                self.search_vehicle()
            elif choice == '6':
                self.delete_vehicle()
            elif choice == '0':
                print("\n✓ Thank you for using Parking Management System")
                self.db.disconnect()
                sys.exit(0)
            else:
                print("✗ Invalid choice. Please try again.")

def main():
    try:
        system = ParkingManagementSystem()
        system.run()
    except KeyboardInterrupt:
        print("\n✗ Application interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
