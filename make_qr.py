import qrcode

# Your exact GitHub Pages live URLs
CLIENT_URL = "https://dennismumo37-cmd.github.io/boda-dispatch-system/client-app/"
RIDER_URL = "https://dennismumo37-cmd.github.io/boda-dispatch-system/rider-app/"

# 1. Generate Client QR Code image
client_qr = qrcode.make(CLIENT_URL)
client_qr.save("client_download_qr.png")

# 2. Generate Rider QR Code image
rider_qr = qrcode.make(RIDER_URL)
rider_qr.save("rider_download_qr.png")

print("✅ Success! QR codes created and saved to your folder.")