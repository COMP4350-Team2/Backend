from locust import HttpUser, task, between

class QuickstartUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def all_api(self):
        # Basic info retrieval
        self.client.get("/api/v3/ingredients")
        self.client.get("/api/v3/measurments")
        # create new user in the database, not enabled currently as no way to delete these
        #self.client.post("/api/v3/user", json={"username":"load_test_user", "email":"load_test_user"})
        
        # Custom ingredient api test
        self.client.post(
            "/api/v3/user/ingredients/custom",
            json={
                "ingredient":"load_test_ingredient",
                "type":"load_test_type"
            }
        )
        self.client.delete("/api/v3/user/ingredients/custom/load_test_ingredient")
        
        # Test lists
        self.client.get("/api/v3/user/lists")
        self.client.post("/api/v3/user/lists/load_test_list")
        self.client.post(
            "/api/v3/user/lists/ingredients",
            json={
                "list_name": "load_test_list",
                "ingredient": "Beef",
                "amount": 500,
                "unit": "g",
                "is_custom_ingredient": False
            }
        )
        self.client.patch(
            "/api/v3/user/lists/ingredients",
            {
                "old_list_name": "load_test_list",
                "old_ingredient": "Beef",
                "old_amount": 500,
                "old_unit": "g",
                "old_is_custom_ingredient": False,
                "new_list_name": "load_test_list",
                "new_ingredient": "Beef",
                "new_amount": 400,
                "new_unit": "lb",
                "new_is_custom_ingredient": False
            }
        )
        self.client.get("/api/v3/user/lists/Grocery")
        self.client.delete(
            "/api/v3/user/lists/ingredients",
            json={
                "ingredient": "Beef",
                "is_custom_ingredient": False,
                "list_name": "load_test_list",
                "unit": "lb"
            }               
        )
        self.client.put(
            "/api/v3/user/lists",
            json={
                "old_list_name": "load_test_list",
                "new_list_name": "load_test_list2"
            }
        )
        self.client.delete("/api/v3/user/lists/load_test_list2")
        
        
        

    #@task(3)
    #def view_items(self):
    #    for item_id in range(10):
    #        self.client.get(f"/item?id={item_id}", name="/item")
    #        time.sleep(1)
    def on_start(self):
        with open(".env") as env_file:
            
        self.client.post("/login/cli", json={"username":"foo", "password":"bar"})