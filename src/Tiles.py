class Land:
    def __init__(self, id, display_name, land_price, color_group) -> None:
        self.id = id
        self.position = id
        self.display_name = display_name
        self.land_price = land_price
        self.buyable = True
        self.tile_type = "land"
        self.has_buildings = False
        self.has_image = False
        self.has_owner = False
        self.house_build_price=50
        self.owner = ""
        self.rent_value = 0
        self.tile_color = "#0003A6"
        self.color_group=color_group
        self.building_details = (
            {
                "owner": "",
                "house": {"number_of_houses": 0, "house_rent": 0},
                "hotels": {"number_of_hotels": 0, "house_rent": 0},
            },
        )

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
            "display_name": self.display_name,
            "land_price": self.land_price,
            "buyable": self.buyable,
            "tile_type": self.tile_type,
            "has_buildings": self.has_buildings,
            "building_details":self.building_details,
            "has_image": self.has_image,
            "has_owner": self.has_owner,
            "owner": self.owner,
            "rent_value": self.rent_value,
            "tile_color": self.tile_color,
            "house_build_price":self.house_build_price
            
        }
        return props
    
    def calculate_house_rent(self):
        n_houses = self.get_house_count()
        
        
        
