import trio
from maltego_trx.maltego import MaltegoTransform, MaltegoMsg
from maltego_trx.transform import DiscoverableTransform
from extensions import registry, twilio_set
from twilio.rest import Client
import csv

def read_account_credentials():
    try:
        with open(".key", "r") as file:
            credentials = file.readlines()

        account_sid = None
        auth_token = None

        for line in credentials:
            key, value = line.strip().split('=')
            if key == "ACCOUNT_SID":
                account_sid = value
            elif key == "AUTH_TOKEN":
                auth_token = value

        if account_sid and auth_token:
            return account_sid, auth_token
        else:
            print("Failed to read account credentials from creds.key.")
    except Exception as e:
        print(f"An error occurred while reading the credentials: {e}")

def carrier_phone_lookup(account_sid: str, auth_token: str, phone_number: str):
    client = Client(account_sid, auth_token)
    response = client.lookups.v2.phone_numbers(phone_number).fetch(fields='line_type_intelligence')

    return response

def get_country_data(country_code):
    try:
        with open('country_data.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['alpha-2'].lower() == country_code.lower():
                    return row
        return None
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
        return None

@registry.register_transform(
    display_name="Get carrier details [twilio]", 
    input_entity="maltego.PhoneNumber",
    description='Returns details from Twilio API lookup for carrier ($/lookup)',
    settings=[],
    output_entities=["maltego.Unknown"],
    transform_set=twilio_set
    )
class toCarrier(DiscoverableTransform):
    
    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):

        async def main():

            # Retrieve number from entity
            phone_number = request.Value

            # Perform Twilio API lookup using stored credentials
            account_sid, auth_token = read_account_credentials()
            lookup = carrier_phone_lookup(account_sid, auth_token, phone_number)

            # Convert results to entities
            if lookup.valid == True:
                number = response.addEntity("maltego.PhoneNumber", value = lookup.phone_number)
                number.addProperty("Valid", value = "True")
                response.addEntity("maltego.Organization", value = lookup.line_type_intelligence["carrier_name"])
                response.addEntity("maltego.Phrase", value = lookup.line_type_intelligence["type"])
                if lookup.line_type_intelligence["mobile_country_code"]:
                    response.addEntity("maltego.AS", value = "MCC# " + str(lookup.line_type_intelligence["mobile_country_code"]))
                if lookup.line_type_intelligence["mobile_network_code"]:
                    response.addEntity("maltego.AS", value = "MNC# " + str(lookup.line_type_intelligence["mobile_network_code"]))

                # Enrich country code data
                country_data = get_country_data(lookup.country_code)
                country = response.addEntity("maltego.Country", value = country_data["name"])
                country.addProperty("location.area", value = country_data["sub-region"])
                country.addProperty("location.areacode", value = country_data["sub-region-code"])
                country.addProperty("countrycode", value = country_data["alpha-2"])
            else:
                response.addEntity("maltego.Phrase", value = "Invalid Number")

        trio.run(main) # running our async code in a non-async code