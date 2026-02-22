import logging
from log import info

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def main():
    logging.info("hass-external-conversation-agent")
    info({"project_name": "hass-external-conversation-agent"})


if __name__ == "__main__":
    main()
