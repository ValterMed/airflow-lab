#!/usr/bin/env python3
"""
# ========================================================================================
# 🚀 MULTI-PRODUCER LAUNCHER - ECOMMERCE EVENT SIMULATOR
# ========================================================================================
#
# PROPÓSITO:
# Ejecutar múltiples instancias del producer.py simultáneamente para simular
# múltiples usuarios generando eventos de e-commerce en paralelo.
#
# CARACTERÍSTICAS:
# - Lanza N procesos productores en paralelo
# - Cada productor simula un conjunto diferente de usuarios
# - Todos envían al mismo tópico de Kafka: ecommerce.events
# - Control centralizado de inicio/detención
# - Logging consolidado
#
# USO:
#   python multi_producer.py --producers 5 --duration 10 --rate 5
# ========================================================================================
"""

import subprocess
import time
import argparse
import logging
import signal
import sys
from typing import List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MultiProducerLauncher:
    """
    Gestor que lanza y controla múltiples instancias de producers simultáneamente.
    """

    def __init__(self, num_producers: int, duration: int, rate: int, kafka_server: str):
        self.num_producers = num_producers
        self.duration = duration
        self.rate = rate
        self.kafka_server = kafka_server
        self.processes: List[subprocess.Popen] = []

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        logger.info("\n🛑 Received interrupt signal, stopping all producers...")
        self.stop_all()
        sys.exit(0)

    def start_all(self):
        """Launch all producer instances"""
        logger.info(f"🚀 Launching {self.num_producers} producers...")
        logger.info(f"📊 Configuration: {self.duration}min @ {self.rate} events/sec each")
        logger.info(f"📡 Kafka server: {self.kafka_server}")
        logger.info(f"🎯 Topic: ecommerce.events")
        logger.info("-" * 70)

        for i in range(1, self.num_producers + 1):
            try:
                # Build command for each producer
                cmd = [
                    "python3",
                    "producer.py",
                    "--stream", "ecommerce",
                    "--duration", str(self.duration),
                    "--rate", str(self.rate),
                    "--kafka-server", self.kafka_server
                ]

                # Launch producer process
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )

                self.processes.append(process)
                logger.info(f"✅ Producer #{i} started (PID: {process.pid})")

                # Small delay between launches to avoid overwhelming Kafka
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"❌ Failed to start producer #{i}: {e}")

        logger.info("-" * 70)
        logger.info(f"✅ All {len(self.processes)} producers launched successfully!")
        logger.info(f"⏱️  Running for {self.duration} minutes...")
        logger.info("🛑 Press Ctrl+C to stop all producers\n")

    def monitor(self):
        """Monitor running producers and display aggregated stats"""
        start_time = time.time()
        end_time = start_time + (self.duration * 60)

        try:
            while time.time() < end_time:
                # Check if all processes are still running
                active_count = sum(1 for p in self.processes if p.poll() is None)

                elapsed = time.time() - start_time
                remaining = end_time - time.time()

                if active_count < len(self.processes):
                    logger.warning(f"⚠️  Only {active_count}/{len(self.processes)} producers still running")

                # Log status every 30 seconds
                if int(elapsed) % 30 == 0 and int(elapsed) > 0:
                    logger.info(f"⏱️  Status: {active_count} producers active | "
                              f"{int(remaining)}s remaining | "
                              f"~{active_count * self.rate} events/sec total")

                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("\n🛑 Monitoring interrupted")

    def wait_for_completion(self):
        """Wait for all producers to finish"""
        logger.info("⏳ Waiting for all producers to complete...")

        for i, process in enumerate(self.processes, 1):
            try:
                returncode = process.wait(timeout=10)
                if returncode == 0:
                    logger.info(f"✅ Producer #{i} completed successfully")
                else:
                    logger.warning(f"⚠️  Producer #{i} exited with code {returncode}")
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️  Producer #{i} timeout, forcing termination...")
                process.kill()

    def stop_all(self):
        """Stop all running producers"""
        logger.info("🛑 Stopping all producers...")

        for i, process in enumerate(self.processes, 1):
            if process.poll() is None:  # Still running
                logger.info(f"   Stopping producer #{i} (PID: {process.pid})...")
                process.terminate()

                # Wait a bit for graceful shutdown
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning(f"   Force killing producer #{i}...")
                    process.kill()

        logger.info("✅ All producers stopped")

    def run(self):
        """Main execution flow"""
        try:
            # Start all producers
            self.start_all()

            # Monitor progress
            self.monitor()

            # Wait for completion
            self.wait_for_completion()

            logger.info("\n" + "="*70)
            logger.info("✅ Multi-producer session completed successfully!")
            logger.info(f"📊 Total producers: {self.num_producers}")
            logger.info(f"⏱️  Duration: {self.duration} minutes")
            logger.info(f"📈 Approx. total events: {self.num_producers * self.rate * self.duration * 60}")
            logger.info("="*70)

        except Exception as e:
            logger.error(f"❌ Error during execution: {e}")
            self.stop_all()
        finally:
            # Ensure all processes are terminated
            for process in self.processes:
                if process.poll() is None:
                    process.kill()


def main():
    """Main entry point with CLI"""
    parser = argparse.ArgumentParser(
        description="Multi-Producer Launcher for E-commerce Events",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch 3 producers, each running for 5 minutes at 5 events/sec
  python multi_producer.py --producers 3 --duration 5 --rate 5

  # Launch 10 producers for intensive load testing
  python multi_producer.py --producers 10 --duration 2 --rate 10

  # Single producer (equivalent to running producer.py directly)
  python multi_producer.py --producers 1 --duration 10 --rate 3
"""
    )

    parser.add_argument(
        "--producers",
        type=int,
        default=3,
        help="Number of producer instances to launch (default: 3)"
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=5,
        help="Duration in minutes for each producer (default: 5)"
    )

    parser.add_argument(
        "--rate",
        type=int,
        default=5,
        help="Events per second per producer (default: 5)"
    )

    parser.add_argument(
        "--kafka-server",
        default="localhost:9092",
        help="Kafka bootstrap server (default: localhost:9092)"
    )

    args = parser.parse_args()

    # Validate arguments
    if args.producers < 1:
        logger.error("❌ Number of producers must be at least 1")
        sys.exit(1)

    if args.duration < 1:
        logger.error("❌ Duration must be at least 1 minute")
        sys.exit(1)

    if args.rate < 1:
        logger.error("❌ Event rate must be at least 1 event/sec")
        sys.exit(1)

    # Launch
    launcher = MultiProducerLauncher(
        num_producers=args.producers,
        duration=args.duration,
        rate=args.rate,
        kafka_server=args.kafka_server
    )

    launcher.run()


if __name__ == "__main__":
    main()
