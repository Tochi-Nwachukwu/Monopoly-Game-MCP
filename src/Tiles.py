from src.constants import tile_constants

class Land:
    def __init__(self, id) -> None:
        self.id = id
        self.position = id
        self.location_name = tile_constants[id]["location_name"]
        self.land_price = tile_constants[id]["land_price"]
        self.buyable = True
        self.tile_type = "land"
        self.has_buildings = False
        self.has_image = False
        self.has_owner = False
        self.house_cost = tile_constants[id]["house_cost"]
        self.owner = ""
        self.rent_value = 0
        self.color_code = tile_constants[id]["color_code"]
        self.house_count = 0
        self.has_hotel = False
        self.mortgage_value = tile_constants[id]["mortgage_value"]

    def get_owner(self):
        return self.owner

    def update_owner(self, owner):
        self.has_owner = True
        self.owner = owner
        return {
            "status": True,
            "message": f"The owner of this property has been updated to {owner}",
        }

    def get_house_count(self):
        return self.building_details["house"]["number_of_houses"]

    def update_rent_value(self):
        no_of_houses = self.building_details["house"]["number_of_houses"]
        house_price = self.building_details["house"]["price_per_house"]
        self.rent_value = no_of_houses * house_price

    def update_houses(self, n_houses):
        current_house_count = self.get_house_count()
        max_houses = 4

        if current_house_count <= max_houses:
            new_house_count = current_house_count + n_houses
            self.building_details["house"]["number_of_houses"] = new_house_count
            return {"status": True, "message": "successfully updated the house count"}
        else:
            self.update_hotels()

    def update_hotels(self):
        self.building_details["hotels"]["number_of_hotels"] += 1

    def get_tile_properties(self):
        props = {
            "id": self.id,
            "position": self.position,
            "location_name": self.location_name,
            "land_price": self.land_price,
            "buyable": self.buyable,
            "tile_type": self.tile_type,
            "has_buildings": self.has_buildings,
            "house_count": self.house_count,
            "has_image": self.has_image,
            "has_owner": self.has_owner,
            "owner": self.owner,
            "rent_value": self.rent_value,
            "color_code": self.color_code,
            "house_cost": self.house_cost,
        }
        return props

    def calculate_house_rent(self):
        n_houses = self.get_house_count()
        rent = tile_constants[id]["rent"][n_houses]
        self.rent_value = rent
        return rent


class Railroad:
    def __init__(self, id) -> None:
        self.owner = ""
        self.id = id
        self.has_owner = False
        self.position = id
        self.location_name = tile_constants[id]["location_name"]
        self.land_price = tile_constants[id]["land_price"]

        def update_owner(self, owner):
            self.has_owner = True
            self.owner = owner
            return {
                "status": True,
                "message": f"The owner of this property has been updated to {owner}",
            }


