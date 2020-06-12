try:
    # Import modules
    from pypresence import Presence, Client
    import time

    # Connect to Discord
    cid = 706083923431522316
    auth = "nV7OxD2xpWnolSxsm9VkGYcmy5re5V"
    rpc = Presence(cid)
    client = Client(cid,pipe=0)
    client.start()
    client.authorize(cid,["rpc","rpc.notifications.read"])
    #client.authenticate(auth)
    print(client.get_selected_voice_channel())
    #client.authorize(cid)
    rpc.connect()
    rpc.update(state="Rich Presence using pypresence!")

    #client.set_user_voice_settings(cid)
    print('RPC set successfully.')

    # Update RPC every 15 seconds
    while True:
        time.sleep(15)

# Custom KeyboardInterrupt message
except KeyboardInterrupt:
    print('\nProgram stopped using Ctrl+C.')
