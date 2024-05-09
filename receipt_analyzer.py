def get_receipt(file):

    #TO DO: add the ability to handle links to images as well for easier analysis


    #initial setup
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer import DocumentAnalysisClient

    endpoint = "https://############.cognitiveservices.azure.com/"
    key = "#################"

    document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    with open(file, "rb") as f:
        poller = document_analysis_client.begin_analyze_document(
            "prebuilt-receipt", document=f, locale="en-US"
        )
    receipts = poller.result()

    #only works for a single reciept picture
    receipt = receipts.documents[0]

    return receipt

def get_items(receipt):

    #TO DO: make sure that if I have a given field once, it always is present or to retake the picture

    import pandas as pd

    #gets items from receipt and stores in pandas dict
    if receipt.fields.get("Items"):
        items = pd.DataFrame()
        confidences = {"item_description": 1,"item_quantity": 1, "item_price": 1, "item_total_price": 1}
        for item in receipt.fields.get("Items").value:
            new_item = {}
            
            item_description = item.value.get("Description")
            if item_description:
                new_item["item_description"] = item_description.value
                confidences["item_description"] = min(item_description.confidence, confidences["item_description"])
        
            item_quantity = item.value.get("Quantity")
            if item_quantity:
                new_item["item_quantity"] = item_quantity.value
                confidences["item_quantity"] = min(item_quantity.confidence, confidences["item_quantity"])

            item_price = item.value.get("Price")
            if item_price:
                new_item["item_price"] = item_price.value
                confidences["item_price"] = min(item_price.confidence, confidences["item_price"])

            item_total_price = item.value.get("TotalPrice")
            if item_total_price:
                new_item["item_total_price"] = item_total_price.value
                confidences["item_total_price"] = min(item_total_price.confidence, confidences["item_total_price"])
                
            items = pd.concat([items, pd.DataFrame([new_item])], ignore_index=True)
                
        return (items,confidences)
    else:
        return None



def print_receipt(receipt):
    receipt_type = receipt.doc_type
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
        for idx, item in enumerate(receipt.fields.get("Items").value):
            print("...Item #{}".format(idx + 1))
            item_description = item.value.get("Description")
            if item_description:
                print(
                    "......Item Description: {} has confidence: {}".format(
                        item_description.value, item_description.confidence
                    )
                )
            item_quantity = item.value.get("Quantity")
            if item_quantity:
                print(
                    "......Item Quantity: {} has confidence: {}".format(
                        item_quantity.value, item_quantity.confidence
                    )
                )
            item_price = item.value.get("Price")
            if item_price:
                print(
                    "......Individual Item Price: {} has confidence: {}".format(
                        item_price.value, item_price.confidence
                    )
                )
            item_total_price = item.value.get("TotalPrice")
            if item_total_price:
                print(
                    "......Total Item Price: {} has confidence: {}".format(
                        item_total_price.value, item_total_price.confidence
                    )
                )
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
