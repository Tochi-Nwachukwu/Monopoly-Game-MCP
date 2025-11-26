chance_cards = [
    {
        "id": 0,
        "content": "Advance to Boardwalk.",
        "action": "move_to_id",
        "destination_id": 39
    },
    {
        "id": 1,
        "content": "Advance to Go (Collect $200).",
        "action": "move_to_id",
        "destination_id": 0,
        "collect_salary": True
    },
    {
        "id": 2,
        "content": "Advance to Illinois Avenue. If you pass Go, collect $200.",
        "action": "move_to_id",
        "destination_id": 24,
        "collect_salary_if_pass_go": True
    },
    {
        "id": 3,
        "content": "Advance to St. Charles Place. If you pass Go, collect $200.",
        "action": "move_to_id",
        "destination_id": 11,
        "collect_salary_if_pass_go": True
    },
    {
        "id": 4,
        "content": "Advance to the nearest Railroad. If unowned, you may buy it from the Bank. If owned, pay owner twice the rental to which they are otherwise entitled.",
        "action": "move_to_nearest",
        "target_type": "railroad",
        "rent_multiplier": 2
    },
    {
        "id": 5,
        "content": "Advance to the nearest Railroad. If unowned, you may buy it from the Bank. If owned, pay owner twice the rental to which they are otherwise entitled.",
        "action": "move_to_nearest",
        "target_type": "railroad",
        "rent_multiplier": 2
    },
    {
        "id": 6,
        "content": "Advance token to nearest Utility. If unowned, you may buy it from the Bank. If owned, throw dice and pay owner a total ten times amount thrown.",
        "action": "move_to_nearest",
        "target_type": "utility",
        "rent_multiplier_rule": "dice_roll_x10"
    },
    {
        "id": 7,
        "content": "Bank pays you dividend of $50.",
        "action": "collect_money",
        "amount": 50
    },
    {
        "id": 8,
        "content": "Get Out of Jail Free.",
        "action": "get_out_of_jail_card",
        "amount": 0
    },
    {
        "id": 9,
        "content": "Go Back 3 Spaces.",
        "action": "move_relative",
        "amount": -3
    },
    {
        "id": 10,
        "content": "Go to Jail. Go directly to Jail, do not pass Go, do not collect $200.",
        "action": "go_to_jail",
        "amount": 0
    },
    {
        "id": 11,
        "content": "Make general repairs on all your property. For each house pay $25. For each hotel pay $100.",
        "action": "general_repairs",
        "house_cost": 25,
        "hotel_cost": 100
    },
    {
        "id": 12,
        "content": "Speeding fine $15.",
        "action": "pay_money",
        "amount": 15
    },
    {
        "id": 13,
        "content": "Take a trip to Reading Railroad. If you pass Go, collect $200.",
        "action": "move_to_id",
        "destination_id": 5,
        "collect_salary_if_pass_go": True
    },
    {
        "id": 14,
        "content": "You have been elected Chairman of the Board. Pay each player $50.",
        "action": "pay_each_player",
        "amount": 50
    },
    {
        "id": 15,
        "content": "Your building loan matures. Collect $150.",
        "action": "collect_money",
        "amount": 150
    }
]