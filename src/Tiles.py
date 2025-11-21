class LandTile:
    def __init__(self, id, display_name, land_price) -> None:
        self.id = id
        self.position = id
        self.display_name = display_name
        self.land_price = land_price
        self.buyable = True
        self.tile_type = "land"
        self.has_buildings = False
        self.has_image = False
        self.has_owner = False
        self.owner = ""
        self.rent_value = 0
        self.color = "#0003A6"
        self.building_details = (
            {
                "owner": "",
                "house": {"number_of_houses": 0, "price_per_house": 0},
                "hotels": {"number_of_hotels": 0, "price_per_hotel": 0},
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
        props = {}
        return props
