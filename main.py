from server.main import HOST, LOG_LEVEL, PORT, TRANSPORT, mcp

if __name__ == "__main__":
    mcp.run(transport=TRANSPORT, host=HOST, port=PORT, log_level=LOG_LEVEL)
