import os
import logging
from locust import HttpUser, task, between
from utils.env_helper import load_env_variables

user_count = 0


class QuickstartUser(HttpUser):
    global user_count
    wait_time = between(1, 5)

    @task
    def all_api(self):
        """
        Sends queries to all cupboard apis.
        """
        # Basic info retrieval
        self.client.get(
            '/api/v3/ingredients',
            headers={'Authorization': 'Bearer ' + self.access_token}
        )

        self.client.get(
            '/api/v3/measurements',
            headers={'Authorization': 'Bearer ' + self.access_token}
        )

        # Custom Ingredients
        self.client.post(
            '/api/v3/user/ingredients/custom',
            headers={'Authorization': 'Bearer ' + self.access_token},
            json={
                'ingredient': 'load_test_ingredient',
                'type': 'load_test_type'
            }
        )

        self.client.delete(
            '/api/v3/user/ingredients/custom/load_test_ingredient',
            headers={'Authorization': 'Bearer ' + self.access_token}
        )

        # Lists
        self.client.get(
            '/api/v3/user/lists',
            headers={'Authorization': 'Bearer ' + self.access_token}
        )

        self.client.post(
            '/api/v3/user/lists/load_test_list',
            headers={'Authorization': 'Bearer ' + self.access_token}
        )

        self.client.post(
            '/api/v3/user/lists/ingredients',
            headers={'Authorization': 'Bearer ' + self.access_token},
            json={
                'list_name': 'load_test_list',
                'ingredient': 'Chewing gum',
                'amount': 500,
                'unit': 'g',
                'is_custom_ingredient': False
            }
        )

        self.client.patch(
            '/api/v3/user/lists/ingredients',
            headers={'Authorization': 'Bearer ' + self.access_token},
            json={
                'old_list_name': 'load_test_list',
                'old_ingredient': 'Chewing gum',
                'old_amount': 500,
                'old_unit': 'g',
                'old_is_custom_ingredient': False,
                'new_list_name': 'load_test_list',
                'new_ingredient': 'Chewing gum',
                'new_amount': 400,
                'new_unit': 'lb',
                'new_is_custom_ingredient': False
            }
        )

        self.client.get(
            '/api/v3/user/lists/load_test_list',
            headers={'Authorization': 'Bearer ' + self.access_token}
        )

        url_string = '/api/v3/user/lists/ingredients'
        url_string += '?list_name=load_test_list&ingredient=Chewing gum'
        url_string += '&unit=lb&is_custom_ingredient=false'
        self.client.delete(
            url_string,
            headers={
                'Authorization': 'Bearer ' + self.access_token,
            }
        )

        self.client.put(
            '/api/v3/user/lists',
            headers={'Authorization': 'Bearer ' + self.access_token},
            json={
                'old_list_name': 'load_test_list',
                'new_list_name': 'load_test_list2'
            }
        )

        self.client.delete(
            '/api/v3/user/lists/load_test_list2',
            headers={'Authorization': 'Bearer ' + self.access_token}
        )

        # Recipes
        self.client.get(
            '/api/v3/user/recipe',
            headers={'Authorization': 'Bearer ' + self.access_token}
        )

        self.client.post(
            '/api/v3/user/recipe/load_test_recipe',
            headers={'Authorization': 'Bearer ' + self.access_token}
        )

        self.client.get(
            '/api/v3/user/recipe/load_test_recipe',
            headers={'Authorization': 'Bearer ' + self.access_token}
        )

        self.client.post(
            '/api/v3/user/recipe/load_test_recipe/ingredient',
            headers={'Authorization': 'Bearer ' + self.access_token},
            json={
                'list_name': 'load_test_list',
                'ingredient': 'Chewing gum',
                'amount': 500,
                'unit': 'g',
                'is_custom_ingredient': False
            }
        )

        url_string = '/api/v3/user/recipe/load_test_recipe/ingredient'
        url_string += '?ingredient=Chewing gum'
        url_string += '&unit=g&is_custom_ingredient=false'
        self.client.delete(
            url_string,
            headers={'Authorization': 'Bearer ' + self.access_token}
        )

        self.client.post(
            '/api/v3/user/recipe/load_test_recipe/step',
            headers={'Authorization': 'Bearer ' + self.access_token},
            json={'step': 'Load test step.'}
        )

        self.client.patch(
            '/api/v3/user/recipe/load_test_recipe/step',
            headers={'Authorization': 'Bearer ' + self.access_token},
            json={'step': 'Load test step 2.', 'step_number': 1}
        )

        self.client.delete(
            '/api/v3/user/recipe/load_test_recipe/step?step_number=1',
            headers={'Authorization': 'Bearer ' + self.access_token}
        )

        self.client.delete(
            '/api/v3/user/recipe/load_test_recipe',
            headers={'Authorization': 'Bearer ' + self.access_token}
        )

    def on_start(self):
        """
        Performs initial login when runner is created.
        """
        global user_count
        user_count = user_count + 1
        self.user_id = user_count
        self.access_token = ''

        if (self.access_token == ''):
            load_env_variables()  # Adds the .env values to environment to allow use

            # Log in user
            print_str = 'Logging User In as user: '
            print_str += str(os.environ['LOAD_TEST_USERNAME'])
            print_str += '_' + str(self.user_id) + '@gmail.com'
            logging.info(print_str)
            username = str(os.environ['LOAD_TEST_USERNAME'])
            username += '_' + str(self.user_id) + '@gmail.com'
            response = self.client.post(
                '/login',
                json={
                    'username': username,
                    'password': os.environ['LOAD_TEST_PASSWORD']
                }
            )
            logging.info(str(response.json()))

            data = response.json()
            self.access_token = data['access_token']
