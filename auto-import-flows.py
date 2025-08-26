#!/usr/bin/env python3
"""
Auto-import Node-RED flows and deploy them
This script waits for Node-RED to start, then imports flows via API
"""

import asyncio
import aiohttp
import json
import time
import sys
import os
from datetime import datetime

# Configuration
NODE_RED_URL = os.getenv("NODE_RED_URL", "http://localhost:1880")
FLOWS_FILE = "flows.json"
MAX_RETRIES = 30
RETRY_INTERVAL = 5  # seconds

class NodeRedAutoImport:
    def __init__(self, node_red_url, flows_file):
        self.node_red_url = node_red_url.rstrip('/')
        self.flows_file = flows_file
        self.session = None
    
    async def wait_for_node_red(self):
        """Wait for Node-RED to be ready"""
        print(f"🔄 Waiting for Node-RED at {self.node_red_url}...")
        
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.node_red_url}/", timeout=aiohttp.ClientTimeout(total=5)) as response:
                        if response.status == 200:
                            print(f"✅ Node-RED is ready! (attempt {attempt})")
                            return True
            except Exception as e:
                print(f"⏳ Attempt {attempt}/{MAX_RETRIES}: Node-RED not ready yet ({str(e)})")
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(RETRY_INTERVAL)
                continue
        
        print(f"❌ Node-RED did not become ready after {MAX_RETRIES} attempts")
        return False
    
    async def get_current_flows(self):
        """Get current flows from Node-RED"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.node_red_url}/flows") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"⚠️ Failed to get current flows: HTTP {response.status}")
                        return None
        except Exception as e:
            print(f"⚠️ Error getting current flows: {e}")
            return None
    
    async def load_flows_file(self):
        """Load flows from JSON file"""
        try:
            with open(self.flows_file, 'r') as f:
                flows = json.load(f)
                print(f"📁 Loaded flows from {self.flows_file}")
                return flows
        except FileNotFoundError:
            print(f"❌ Flows file not found: {self.flows_file}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in flows file: {e}")
            return None
    
    async def import_flows(self, flows):
        """Import flows to Node-RED"""
        try:
            # Node-RED expects flows as a direct array, not wrapped in an object
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.node_red_url}/flows",
                    json=flows,  # Send flows directly as array
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status in [200, 204]:
                        print("✅ Flows imported successfully!")
                        return True
                    else:
                        response_text = await response.text()
                        print(f"❌ Failed to import flows: HTTP {response.status}")
                        print(f"Response: {response_text}")
                        return False
        except Exception as e:
            print(f"❌ Error importing flows: {e}")
            return False
    
    async def deploy_flows(self):
        """Deploy the flows"""
        try:
            deploy_data = {"type": "full"}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.node_red_url}/flows",
                    json=deploy_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status in [200, 204]:
                        print("🚀 Flows deployed successfully!")
                        return True
                    else:
                        response_text = await response.text()
                        print(f"❌ Failed to deploy flows: HTTP {response.status}")
                        print(f"Response: {response_text}")
                        return False
        except Exception as e:
            print(f"❌ Error deploying flows: {e}")
            return False
    
    async def verify_endpoints(self):
        """Verify that the imported endpoints are working"""
        endpoints_to_test = ["/sensors", "/devices", "/status"]
        
        print("🧪 Verifying imported endpoints...")
        
        all_working = True
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints_to_test:
                try:
                    async with session.get(f"{self.node_red_url}{endpoint}") as response:
                        if response.status == 200:
                            print(f"✅ {endpoint} - Working")
                        else:
                            print(f"❌ {endpoint} - HTTP {response.status}")
                            all_working = False
                except Exception as e:
                    print(f"❌ {endpoint} - Error: {e}")
                    all_working = False
        
        return all_working
    
    async def check_flows_exist(self):
        """Check if flows already exist"""
        current_flows = await self.get_current_flows()
        if not current_flows:
            return False
        
        # Check if our specific flows exist
        flow_tabs = [flow for flow in current_flows if flow.get("type") == "tab"]
        api_endpoints_tab = any(tab.get("label") == "API Endpoints" for tab in flow_tabs)
        
        if api_endpoints_tab:
            print("ℹ️ API Endpoints flows already exist")
            return True
        
        return False
    
    async def run(self):
        """Main execution function"""
        print("🚀 Node-RED Auto-Import Starting...")
        print(f"⏰ Started at: {datetime.now().isoformat()}")
        print(f"🎯 Target: {self.node_red_url}")
        print(f"📂 Flows file: {self.flows_file}")
        print("=" * 60)
        
        # Step 1: Wait for Node-RED to be ready
        if not await self.wait_for_node_red():
            return False
        
        # Step 2: Check if flows already exist
        if await self.check_flows_exist():
            print("✅ Flows already imported and working!")
            
            # Still verify endpoints work
            if await self.verify_endpoints():
                print("🎉 All endpoints are working correctly!")
                return True
            else:
                print("⚠️ Some endpoints not working, will re-import...")
        
        # Step 3: Load flows from file
        flows = await self.load_flows_file()
        if not flows:
            return False
        
        # Step 4: Import flows
        if not await self.import_flows(flows):
            return False
        
        # Step 5: Wait a moment for flows to be processed
        print("⏳ Waiting for flows to be processed...")
        await asyncio.sleep(3)
        
        # Step 6: Verify endpoints
        if await self.verify_endpoints():
            print("🎉 Auto-import completed successfully!")
            print("🔗 Available endpoints:")
            print(f"   • {self.node_red_url}/sensors")
            print(f"   • {self.node_red_url}/devices")
            print(f"   • {self.node_red_url}/status")
            print(f"   • {self.node_red_url}/data")
            print(f"   • {self.node_red_url}/control (POST)")
            return True
        else:
            print("❌ Some endpoints are not working properly")
            return False

async def main():
    """Main function"""
    
    # Check if flows file exists
    if not os.path.exists(FLOWS_FILE):
        print(f"❌ Flows file '{FLOWS_FILE}' not found!")
        print("Make sure the flows.json file is in the same directory as this script.")
        sys.exit(1)
    
    # Create auto-importer
    importer = NodeRedAutoImport(NODE_RED_URL, FLOWS_FILE)
    
    try:
        success = await importer.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\\n⏹️ Auto-import interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        sys.exit(3)

if __name__ == "__main__":
    # Check if aiohttp is available
    try:
        import aiohttp
    except ImportError:
        print("❌ aiohttp is required for this script.")
        print("Install it with: pip3 install aiohttp")
        sys.exit(4)
    
    asyncio.run(main())
