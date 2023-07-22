import asyncio
import websockets
import sys

async def exchange_rates():
    if len(sys.argv) < 4:
        print("Usage: python client.py exchange <num_days> <currency1> <currency2> ...")
        return

    command = " ".join(sys.argv[1:])
    uri = "ws://localhost:8765"

    async with websockets.connect(uri) as websocket:
        await websocket.send(command)
        print(f">>> {command}")

        response = await websocket.recv()
        print("Current exchange rates:")
        print(response)

if __name__ == "__main__":
    asyncio.run(exchange_rates())
