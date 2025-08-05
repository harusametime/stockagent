# Stock Trading Agent

A comprehensive trading system for Nikkei 225 ETFs (1579.T and 1360.T) with backtesting, algorithmic trading, and web interface.

## Features

1. **Backtesting Engine** - Test trading algorithms with historical data
2. **Trading Algorithms** - Technical analysis based strategies
3. **Live Trading** - Execute trades via KabusAPI
4. **Web Interface** - Streamlit-based dashboard

## ETFs

- **1579.T** - Nikkei 225 ETF (increases when Nikkei 225 rises)
- **1360.T** - Inverse Nikkei 225 ETF (decreases when Nikkei 225 rises)

## Installation

### Option 1: Local Installation

```bash
pip install -r requirements.txt
```

### Option 2: Docker Installation (Recommended)

```bash
# Build and start the application
./docker-run.sh build
./docker-run.sh start

# Or use docker-compose directly
docker-compose up -d
```

## Usage

### Local Usage

1. Run backtesting: `python test_backtesting.py`
2. Run web interface: `streamlit run app.py`

### Docker Usage

```bash
# Start the application
./docker-run.sh start

# View logs
./docker-run.sh logs

# Run tests
./docker-run.sh test

# Run backtesting
./docker-run.sh backtest

# Stop the application
./docker-run.sh stop

# Show help
./docker-run.sh help
```

### Alternative: Using Makefile

```bash
# Quick start (build and start)
make quick-start

# Individual commands
make build
make start
make stop
make logs
make test
make backtest

# Show all available commands
make help
```

## Configuration

Create a `.env` file with your API credentials:

```
KABUSAPI_HOST=your_host
KABUSAPI_PORT=your_port
KABUSAPI_PASSWORD=your_password
```

### Docker Environment Variables

The following environment variables can be set in your `.env` file or passed to Docker:

- `KABUSAPI_HOST`: KabusAPI host (default: localhost)
- `KABUSAPI_PORT`: KabusAPI port (default: 18080)
- `KABUSAPI_PASSWORD`: KabusAPI password
- `INITIAL_CAPITAL`: Initial trading capital (default: 1000000)
- `MAX_POSITION_SIZE`: Maximum position size (default: 500000)
- `STOP_LOSS_PCT`: Stop loss percentage (default: 5)
- `TAKE_PROFIT_PCT`: Take profit percentage (default: 10)
- `MAX_DAILY_TRADES`: Maximum daily trades (default: 10) 