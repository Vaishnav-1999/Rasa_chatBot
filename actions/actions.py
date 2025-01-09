import logging
import random
import time
from tkinter import EventType
import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from sanic import Sanic, response 
from sanic_cors import CORS
from rasa_sdk.types import DomainDict
from rasa_sdk.events import AllSlotsReset, Form
from rasa_sdk.forms import FormValidationAction
import os


# Order number Validation

class ValidateTrackOrderForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_track_order_form"

    def validate_order_number(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate order_number value."""

        if value:  # You can add more validation logic here
            return {"order_number": value}
        else:
            dispatcher.utter_message(text="Please provide a valid order number.")
            return {"order_number": None}

# Fetching Order_Details using Mobile Number.

class OrderDetailsAction(Action):
    def name(self) -> Text:
        return "action_order_details"

    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        logging.info("OrderDetailsAction is being called")

        # Get the slot value from the tracker
        value = next(tracker.get_latest_entity_values("mobileNo"), None) #extracts mobile  numbers

        data = {
            "mobileNumber": value
            
        }

        # URL where the POST request is to be sent
        api_url = "http://192.168.50.47:8087/credeze/orders/cg/order-details"
        
        try:
            response = requests.post(api_url, json=data)

            if response.status_code == 200:
                api_response = response.json()
                order_details = api_response.get("orderDetails", [])

                if order_details:
                    formatted_details = "\n".join([
                        f"Order Date: {order['orderDate']}\n"
                        f"Order ID: {order['orderNo']}\n"
                        f"Order Items: {', '.join([item['productName'] for item in order['orderItems']])}\n"
                        for order in order_details
                    ])
                    dispatcher.utter_message(f"Order details:\n{formatted_details}")
                    return [SlotSet("api_response", api_response)]
                else:
                    dispatcher.utter_message(text="No order details found.")
                    return []
            else:
                dispatcher.utter_message(text="Failed to fetch your data.")
                return []

        except Exception as e:
            dispatcher.utter_message(text=f"Error occurred: {str(e)}")
            
        return[]


# Fetching order status using Order_number.

class OrderStatusAction(Action):
    def name(self) -> Text:
        return "action_order_status"

    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        logging.info("OrderStatusAction is being called")

        # Get the slot value from the tracker
        order_number = next(tracker.get_latest_entity_values("order_number"), None)

        data = {
            "filterVal": order_number
        }

        # URL where the POST request is to be sent
        api_url = "http://192.168.50.47:8087/credeze/orders/cg/order-status"
        
        try:
            response = requests.post(api_url, json=data)

            if response.status_code == 200:
                api_response = response.json()
                status_value = api_response.get("value", None)

                if status_value:
                    dispatcher.utter_message(text=f"Your order status is {status_value}.")
                    return [SlotSet("api_response", api_response)]
                else:
                    dispatcher.utter_message(text="No order details found.")
                    return []
            else:
                dispatcher.utter_message(text="Failed to fetch your data.")
                return []

        except Exception as e:
            dispatcher.utter_message(text=f"Error occurred: {str(e)}")
            
        return []
    
# Add review

class ActionSubmitReview(Action):
    def name(self) -> str:
        return "action_submit_review"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        order_item_reference = tracker.get_slot("order_item_reference")
        rating = tracker.get_slot("rating")
        review_comment = tracker.get_slot("review_comment")

        logging.info("action_submit_review is being called")

        url = "http://192.168.50.47:8087/credeze/orders/cg/order-review-from-bot"
        payload = {
            "reqSecureKey": order_item_reference,
            "lobType": review_comment,
            "filterVal": rating
        }

        response = requests.post(url, json=payload)
        response_data = response.json()

        value = response_data.get("value", "") or ""
        logging.info(value.lower())


        # logging.info(response_data.get("value", "").lower())

        if value.lower() == "request processed successfully.":
            dispatcher.utter_message(text="Review added successfully.")
            return [
                SlotSet("order_item_reference", None),
                SlotSet("rating", None),
                SlotSet("review_comment", None),
                SlotSet("api_response", "success")
            ]
        else:
            dispatcher.utter_message(text="Adding review failed.")
            return [
                SlotSet("order_item_reference", None),
                SlotSet("rating", None),
                SlotSet("review_comment", None),
                SlotSet("api_response", "failure")
            ]

        return []

# Validating review form

class ValidateReviewForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_review_form"

    def validate_order_item_reference(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate `order_item_reference` value."""

        if value:  # Add your validation logic here
            return {"order_item_reference": value}
        else:
            dispatcher.utter_message(text="Invalid order item reference.")
            return {"order_item_reference": None}

    def validate_rating(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate `rating` value."""

        if value.isdigit() and 1 <= int(value) <= 5:
            return {"rating": value}
        else:
            dispatcher.utter_message(text="Rating must be a number between 1 and 5.")
            return {"rating": None}

    def validate_review_comment(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate `review_comment` value."""

        if value:
            return {"review_comment": value}
        else:
            dispatcher.utter_message(text="Review comment cannot be empty.")
            return {"review_comment": None}
        
# Deactivate order Form
class ActionDeactivateForm(Action):
    def name(self) -> str:
        return "action_deactivate_form"

    def run(self, dispatcher, tracker, domain):
        return [Form(None), AllSlotsReset()]
    
# Continuing Bot flow

# class ActionAskFurtherAssistance(Action):
#     def name(self) -> Text:
#         return "action_ask_further_assistance"

#     def run(self, dispatcher, tracker, domain):
#         dispatcher.utter_message(response="utter_ask_further_assistance")
#         return []

# class ActionHappyToHelp(Action):
#     def name(self) -> Text:
#         return "action_happy_to_help"

#     def run(self, dispatcher, tracker, domain):
#         dispatcher.utter_message(response="utter_happy_to_help")
#         return []

# Extracting Name from the User's Input.

class ActionSaveName(Action):
    def name(self) -> str:
        return "action_save_name"

    def run(self, dispatcher, tracker, domain):
        # Get the user's latest input
        user_name = tracker.latest_message.get("text")

        # Validate if the input is empty or invalid (optional)
        if not user_name or user_name.lower() in ["hi", "hello", "hey"]:
            dispatcher.utter_message(text="That doesn't seem like a name. Could you please tell me your name?")
            return []

        # Acknowledge the name and save it in the slot
        dispatcher.utter_message(text=f"Got it, {user_name}. Nice to meet you!")
        return [SlotSet("name", user_name)]


class ActionAskName(Action):
    def name(self) -> Text:
        return "action_ask_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(template="utter_ask_name")
        return []

class ActionHandleFeedback(Action):
    def name(self) -> Text:
        return "action_handle_feedback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        feedback = tracker.get_slot('feedback')
        dispatcher.utter_message(template="utter_happy_to_help")
        return [SlotSet("feedback", feedback)]

class OrderDetailsAction(Action):
    def name(self) -> Text:
        return "action_order_details"

    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get the slot value from the tracker
        value = next(tracker.get_latest_entity_values("mobileNo"), None) #extracts mobile  numbers

        data = {
            "mobileNumber": value
            
        }

        # URL where the POST request is to be sent
        api_url = "http://192.168.50.47:8087/credeze/orders/cg/bot-order-details"
        
        try:
            response = requests.post(api_url, json=data)

            if response.status_code == 200:
                api_response = response.json()
                order_details = api_response.get("orderDetails", [])

                if order_details:
                    formatted_details = "\n".join([
                        f"Order Date: {order['orderDate']}\n"
                        f"Order ID: {order['orderNo']}\n"
                        f"Order Items: {', '.join([item['productName'] for item in order['orderItems']])}\n"
                        for order in order_details
                    ])
                    dispatcher.utter_message(f"Order details:\n{formatted_details}")
                    return [SlotSet("api_response", api_response)]
                else:
                    dispatcher.utter_message(text="No order details found.")
                    return []
            else:
                dispatcher.utter_message(text="Failed to fetch your data.")
                return []

        except Exception as e:
            dispatcher.utter_message(text=f"Error occurred: {str(e)}")
            
        return[]

class ActionAskMobileNumber(Action):
    def name(self) -> Text:
        return "action_ask_mobile_number"

    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="Please enter your mobile number to retrieve your previous orders.")
        return []
    
class OrderDetailsAction(Action):
    def name(self) -> Text:
        return "action_order_details"

    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        logging.info("OrderDetailsAction is being called")

        # Get the slot value from the tracker
        value = next(tracker.get_latest_entity_values("mobileNo"), None) #extracts mobile  numbers

        data = {
            "mobileNumber": value
            
        }

        # URL where the POST request is to be sent
        api_url = "http://192.168.50.47:8087/credeze/orders/cg/order-details"
        
        try:
            response = requests.post(api_url, json=data)

            if response.status_code == 200:
                api_response = response.json()
                order_details = api_response.get("orderDetails", [])

                if order_details:
                    formatted_details = "\n".join([
                        f"Order Date: {order['orderDate']}\n"
                        f"Order ID: {order['orderNo']}\n"
                        f"Order Items: {', '.join([item['productName'] for item in order['orderItems']])}\n"
                        for order in order_details
                    ])
                    dispatcher.utter_message(f"Order details:\n{formatted_details}")
                    return [SlotSet("api_response", api_response)]
                else:
                    dispatcher.utter_message(text="No order details found.")
                    return []
            else:
                dispatcher.utter_message(text="Failed to fetch your data.")
                return []

        except Exception as e:
            dispatcher.utter_message(text=f"Error occurred: {str(e)}")
            
        return[]
    
    # New Additions

# class ActionHandleMobileNumber(Action):
#     def name(self) -> Text:
#         return "action_handle_mobile_number"

#     def run(self, dispatcher: CollectingDispatcher, 
#             tracker: Tracker, 
#             domain: Dict[Text, Any]) -> List[EventType]:
        
#         mobile_number = tracker.get_slot('mobileNo')
#         dispatcher.utter_message(text=f"Thank you! Your mobile number is {mobile_number}.")
#         return []

class TrackFlightStatusAction(Action):
    def name(self) -> Text:
        return "action_flight_status"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logging.info("TrackFlightStatusAction is being called")

        # Get the slot value from the tracker
        pnr = next(tracker.get_latest_entity_values("pnr"), None)

        if pnr is None:
            dispatcher.utter_message(text="Please provide your PNR to track your flight.")
            return []

        data = {
            "filterVal": pnr
        }

        # URL where the POST request is to be sent
        api_url = "http://192.168.50.47:6055/credeze/travel/packages/maint/flight-status"

        try:
            response = requests.post(api_url, json=data)

            if response.status_code == 200:
                api_response = response.json()
                status_value = api_response.get("value", None)
                logging.info(status_value);
                if status_value:
                    dispatcher.utter_message(text=f"Your flight status is {status_value}.")
                    return [SlotSet("flight_status_response", api_response)]
                else:
                    dispatcher.utter_message(text="No flight details found.")
                    return []
            else:
                dispatcher.utter_message(text="Failed to fetch flight status.")
                return []

        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
            dispatcher.utter_message(text="An error occurred while trying to fetch flight status.")
            return []

# New Additions - Flight Booking

class ActionFlightBookingHistory(Action):
    def name(self) -> Text:
        return "action_flight_booking_history"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Retrieve the mobile number from the slot
        mobile_number = tracker.get_slot('mobileNo')
        
        if mobile_number:
            # Define the API endpoint and data payload
            api_url = "http://192.168.50.47:6055/credeze/travel/packages/maint/flight-list"
            payload = {
                "mobileNumber": mobile_number  # Assuming the API expects a 'filterVal' key with the mobile number
            }

            try:
                # Make the API call
                response = requests.post(api_url, json=payload)

                if response.status_code == 200:
                    api_response = response.json()
                    # Extract the flight booking details
                    flight_details = api_response.get("journeyList", [])  # Assuming the key is "flightDetails"

                    if flight_details:
                        # Format the flight details for user-friendly output
                        formatted_flight_details = "\n\n".join([
                            f"Booking Number: {flight['bookingNumber']}\n"
                            f"Air PNR: {flight['airPnr']}\n"
                            f"Flight Status: {flight['flightStatus']}\n"
                            for flight in flight_details
                        ])
                        dispatcher.utter_message(f"Here are your flight booking details:\n\n{formatted_flight_details}")
                        return [SlotSet("api_response", api_response)]
                    else:
                        dispatcher.utter_message("No flight booking history found for your details.")
                else:
                    dispatcher.utter_message("Failed to retrieve flight booking history. Please try again later.")
            except requests.exceptions.RequestException as e:
                dispatcher.utter_message("An error occurred while fetching your flight booking history.")
                print(f"Error fetching flight booking history: {e}")
        else:
            # If neither PNR nor mobile number is provided, prompt user to provide details
            dispatcher.utter_message("Please provide your PNR or mobile number to retrieve flight booking history.")
            return [SlotSet("pnr", None), SlotSet("mobileNo", None)]  # Optionally reset slots

        return []

# Service Booking

class ActionServiceBookingHistory(Action):
    def name(self) -> Text:
        return "action_service_booking_history"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Retrieve the mobile number from the slot
        mobile_number = tracker.get_slot('mobileNo')
        
        if mobile_number:
            # Define the API endpoint and data payload
            api_url = "http://192.168.50.47:6056/credeze/dailyservice/service-list"
            payload = {
                "mobileNumber": mobile_number  # Assuming the API expects a 'mobileNumber' key with the mobile number
            }

            try:
                # Make the API call
                response = requests.post(api_url, json=payload)

                if response.status_code == 200:
                    api_response = response.json()
                    # Extract the service booking details
                    service_list = api_response.get("serviceList", [])  # Assuming the key is "serviceList"

                    if service_list:
                        # Format the service details for user-friendly output
                        formatted_service_details = "\n\n".join([
                            f"Booking Number: {service['bookingNumber']}\n"
                            f"Status: {service['status']}\n"
                            f"Service Type: {service['serviceType']}\n"
                            for service in service_list
                        ])
                        dispatcher.utter_message(f"Here are your service booking details:\n\n{formatted_service_details}")
                        return [SlotSet("api_response", api_response)]
                    else:
                        dispatcher.utter_message("No service booking history found for your details.")
                else:
                    dispatcher.utter_message("Failed to retrieve service booking history. Please try again later.")
            except requests.exceptions.RequestException as e:
                dispatcher.utter_message("An error occurred while fetching your service booking history.")
                print(f"Error fetching service booking history: {e}")
        else:
            # If no mobile number is provided, prompt the user to provide details
            dispatcher.utter_message("Please provide your mobile number to retrieve service booking history.")
            return [SlotSet("mobileNo", None)]  # Optionally reset slots

        return []


# Services Api to fetch status

class ActionServiceStatus(Action):
    def name(self) -> Text:
        return "action_service_status"

    def run(self, dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        logging.info("ActionServiceStatus is being called")

        # Get the slot value from the tracker
        booking_number = next(tracker.get_latest_entity_values("booking_number"), None)

        data = {
            "filterVal": booking_number
        }

        # URL where the POST request is to be sent
        api_url = "http://192.168.50.47:6056/credeze/dailyservice/service-status"
        
        try:
            response = requests.post(api_url, json=data)

            if response.status_code == 200:
                api_response = response.json()
                status_value = api_response.get("value", None)

                if status_value:
                    dispatcher.utter_message(text=f"Your service status is {status_value}.")
                    return [SlotSet("api_response", api_response)]
                else:
                    dispatcher.utter_message(text="No service details found.")
                    return []
            else:
                dispatcher.utter_message(text="Failed to fetch your service status. Please try again later.")
                return []

        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred while fetching your service status: {str(e)}")
            logging.error(f"Error in ActionServiceStatus: {e}")
            
        return []


# Adding and retriveing Promotions 

class ActionPromotionsCoupons(Action):
    def name(self):
        return "action_promotions_coupons"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="Here are the latest promotions and coupons!")

        image_urls = [
            "https://static3.bigstockphoto.com/2/8/6/large2/68251495.jpg"
        ]

        for url in image_urls:
            dispatcher.utter_message(image=url)

        return []

# class ActionPromotionsCoupons(Action):
#     def name(self):
#         return "action_promotions_coupons"

#     def run(self, dispatcher: CollectingDispatcher, tracker, domain):
#         # Define the folder containing the images
#         image_folder = "images/promotions/"

#         try:
#             # Ensure the folder exists
#             if not os.path.exists(image_folder):
#                 dispatcher.utter_message(text="No promotions are available at the moment.")
#                 return []

#             # List all files in the folder
#             image_files = [f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]

#             # Randomly pick an image
#             if image_files:
#                 selected_image = random.choice(image_files)
#                 image_url = f"http://192.168.0.234:5000/images/{selected_image}"  # Adjust based on your server
#             else:
#                 image_url = None

#             # Send the response
#             if image_url:
#                 dispatcher.utter_message(
#                     text="Here are the latest promotions and coupons!",
#                     image=image_url
#                 )
#             else:
#                 dispatcher.utter_message(text="No promotions are available at the moment.")
#         except Exception as e:
#             # Handle unexpected errors gracefully
#             dispatcher.utter_message(text=f"An error occurred while fetching promotions: {str(e)}")

#         return []


# Retriving Promotions

class ActionDownloadInvoice(Action):
    def name(self):
        return "action_download_invoice"

    def run(self, dispatcher, tracker, domain):
        # Provide the static file download link
        file_url = "http://192.168.0.234:5000/static/apache_kafka_tutorial.pdf"
        dispatcher.utter_message(text="You can download your invoice here:", attachment=file_url)
        return []




