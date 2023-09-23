"""
This code sample shows Prebuilt Receipt operations with the Azure Form Recognizer client library. 
The async versions of the samples require Python 3.6 or later.

To learn more, please visit the documentation - Quickstart: Form Recognizer Python client library SDKs
https://docs.microsoft.com/en-us/azure/applied-ai-services/form-recognizer/quickstarts/try-v3-python-sdk
"""



from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import pandas as pd


"""
Remember to remove the key from your code when you're done, and never post it publicly. For production, use
secure methods to store and access your credentials. For more information, see 
https://docs.microsoft.com/en-us/azure/cognitive-services/cognitive-services-security?tabs=command-line%2Ccsharp#environment-variables-and-application-configuration
"""
endpoint = "https://datacollector.cognitiveservices.azure.com/"
key = "725146f09b434fa2b8ec78290a50b516"

# sample document
file = "test receipt.jpg"

document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)


with open(file, "rb") as f:
        poller = document_analysis_client.begin_analyze_document(
            "prebuilt-receipt", document=f, locale="en-US"
        )

#poller = document_analysis_client.begin_analyze_document("prebuilt-receipt", file)

receipts = poller.result()

#only works for a single reciept picture
receipt = receipts.documents[0]

receipt_type = receipt.doc_type.split('.')[-1]
if receipt_type:
    print(
        "Receipt Type: {}".format(receipt_type)
    )
merchant_name = receipt.fields.get("MerchantName")
if merchant_name:
    print(
        "Merchant Name: {} has confidence: {}".format(
            merchant_name.value, merchant_name.confidence
        )
    )
transaction_date = receipt.fields.get("TransactionDate")
if transaction_date:
    print(
        "Transaction Date: {} has confidence: {}".format(
            transaction_date.value, transaction_date.confidence
        )
    )
if receipt.fields.get("Items"):
    print("Receipt items:")
    items = pd.DataFrame()
    for idx, item in enumerate(receipt.fields.get("Items").value):
        # print("...Item #{}".format(idx + 1))
        item_description = item.value.get("Description")
        item_quantity = item.value.get("Quantity")
        item_price = item.value.get("Price")
        item_total_price = item.value.get("TotalPrice")
        confidence = []
        #print(item_quantity.value)
        new_item = {"item_description": item_description.value if item_description else None,
                "item_quantity" : item_quantity.value if item_quantity else None,
                "item_price" : item_price.value if item_price else None,
                "item_total_price" : item_total_price.value if item_total_price else None}
    
        items = pd.concat([items, pd.DataFrame([new_item])], ignore_index=True)
    print(items)
subtotal = receipt.fields.get("Subtotal")
if subtotal:
    print(
        "Subtotal: {} has confidence: {}".format(
            subtotal.value, subtotal.confidence
        )
    )
tax = receipt.fields.get("TotalTax")
if tax:
    print("Tax: {} has confidence: {}".format(tax.value, tax.confidence))
tip = receipt.fields.get("Tip")
if tip:
    print("Tip: {} has confidence: {}".format(tip.value, tip.confidence))
total = receipt.fields.get("Total")
if total:
    print("Total: {} has confidence: {}".format(total.value, total.confidence))
print("--------------------------------------")
