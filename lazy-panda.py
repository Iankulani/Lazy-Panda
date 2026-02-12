#!/usr/bin/env python3
"""
🐼 LAZY PANDA
Author: Ian Carter Kulani
Description: One command to ping, trace, scan, and locate any IP address
Single command: panda <ip> - Does everything automatically
"""

import os
import sys
import json
import time
import socket
import subprocess
import platform
import requests
import shutil
import ipaddress
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# =====================
# COLOR CONFIGURATION
# =====================
class Colors:
    RED = Fore.RED + Style.BRIGHT
    GREEN = Fore.GREEN + Style.BRIGHT
    YELLOW = Fore.YELLOW + Style.BRIGHT
    BLUE = Fore.BLUE + Style.BRIGHT
    CYAN = Fore.CYAN + Style.BRIGHT
    MAGENTA = Fore.MAGENTA + Style.BRIGHT
    WHITE = Fore.WHITE + Style.BRIGHT
    RESET = Style.RESET_ALL

# =====================
# LAZY PANDA - SINGLE COMMAND TOOL
# =====================
class LazyPanda:
    """🐼 One command to rule them all - Ping, Trace, Scan, Locate"""
    
    def __init__(self):
        self.results = {
            'target': '',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ping': {},
            'traceroute': {},
            'scan': {},
            'location': {},
            'system': {}
        }
    
    def print_banner(self):
        """Print lazy panda banner"""
        banner = f"""
{Colors.GREEN}╔══════════════════════════════════════════════════════════════════╗
║{Colors.WHITE}                      🐼 LAZY PANDA                          {Colors.GREEN}║
║{Colors.WHITE}              One Command - Everything Automated                {Colors.GREEN}║
╠══════════════════════════════════════════════════════════════════╣
║{Colors.CYAN}  • Ping Test     • Traceroute    • Port Scan                   {Colors.GREEN}║
║{Colors.CYAN}  • IP Location   • OS Detection  • Service Detection           {Colors.GREEN}║
╚══════════════════════════════════════════════════════════════════╝{Colors.RESET}
        """
        print(banner)
    
    def run(self, target):
        """Execute all scans on target - THE ONE COMMAND"""
        
        # Validate target
        try:
            # Check if it's an IP
            ipaddress.ip_address(target)
            is_ip = True
        except:
            is_ip = False
        
        self.results['target'] = target
        print(f"\n{Colors.YELLOW}🎯 Target: {Colors.WHITE}{target}{Colors.RESET}")
        print(f"{Colors.YELLOW}⏰ Time: {Colors.WHITE}{self.results['timestamp']}{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")
        
        # 1. PING TEST
        self._ping_target(target)
        
        # 2. TRACEROUTE
        self._traceroute_target(target)
        
        # 3. PORT SCAN
        self._scan_target(target)
        
        # 4. IP LOCATION (only if it's an IP)
        if is_ip:
            self._locate_ip(target)
        else:
            # Try to resolve domain to IP
            try:
                ip = socket.gethostbyname(target)
                print(f"{Colors.GREEN}🌐 Domain resolved to: {Colors.WHITE}{ip}{Colors.RESET}")
                self._locate_ip(ip)
            except:
                print(f"{Colors.YELLOW}⚠️ Cannot locate domain - not an IP address{Colors.RESET}")
        
        # 5. SYSTEM INFO
        self._get_system_info()
        
        # 6. SAVE REPORT
        self._save_report()
        
        # 7. PRINT SUMMARY
        self._print_summary()
        
        return self.results
    
    def _ping_target(self, target):
        """Ping the target"""
        print(f"{Colors.BLUE}📡 Pinging {target}...{Colors.RESET}")
        
        try:
            if platform.system().lower() == 'windows':
                cmd = ['ping', '-n', '4', target]
            else:
                cmd = ['ping', '-c', '4', target]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            ping_time = time.time() - start_time
            
            # Parse ping statistics
            output = result.stdout + result.stderr
            success = result.returncode == 0
            
            # Extract packet loss and RTT
            packet_loss = "N/A"
            rtt_min = rtt_avg = rtt_max = "N/A"
            
            if "loss" in output.lower():
                for line in output.split('\n'):
                    if "loss" in line.lower():
                        packet_loss = line.strip()
                    if "rtt" in line.lower() or "round-trip" in line.lower():
                        rtt_values = line.split('=')[1].strip() if '=' in line else "N/A"
                        if '/' in str(rtt_values):
                            parts = rtt_values.split('/')
                            if len(parts) >= 4:
                                rtt_min, rtt_avg, rtt_max = parts[0], parts[1], parts[2]
            
            self.results['ping'] = {
                'success': success,
                'output': output[:500],
                'packet_loss': packet_loss,
                'rtt_min': rtt_min,
                'rtt_avg': rtt_avg,
                'rtt_max': rtt_max,
                'time': round(ping_time, 2)
            }
            
            if success:
                print(f"{Colors.GREEN}  ✅ Ping successful{Colors.RESET}")
                print(f"  📊 Packet Loss: {Colors.WHITE}{packet_loss}{Colors.RESET}")
                if rtt_avg != "N/A":
                    print(f"  ⏱️  RTT: {Colors.WHITE}{rtt_avg} avg{Colors.RESET}")
            else:
                print(f"{Colors.RED}  ❌ Ping failed{Colors.RESET}")
                
        except subprocess.TimeoutExpired:
            self.results['ping'] = {'success': False, 'error': 'Timeout'}
            print(f"{Colors.RED}  ❌ Ping timeout{Colors.RESET}")
        except Exception as e:
            self.results['ping'] = {'success': False, 'error': str(e)}
            print(f"{Colors.RED}  ❌ Ping error: {str(e)[:50]}{Colors.RESET}")
        
        print()
    
    def _traceroute_target(self, target):
        """Traceroute to target"""
        print(f"{Colors.MAGENTA}🛣️  Tracing route to {target}...{Colors.RESET}")
        
        try:
            if platform.system().lower() == 'windows':
                cmd = ['tracert', '-d', '-h', '15', target]
            else:
                # Try traceroute, if not available use tracepath
                if shutil.which('traceroute'):
                    cmd = ['traceroute', '-n', '-m', '15', target]
                elif shutil.which('tracepath'):
                    cmd = ['tracepath', '-m', '15', target]
                else:
                    raise Exception("No traceroute tool found")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
            output = result.stdout + result.stderr
            
            # Parse hops
            hops = []
            lines = output.split('\n')
            for line in lines:
                if platform.system().lower() == 'windows':
                    if 'ms' in line and len(line) > 10:
                        hops.append(line.strip())
                else:
                    # Unix-like output
                    if ' 1 ' in line or ' 2 ' in line or ' 3 ' in line or ' 4 ' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            hops.append(f"{parts[0]}: {' '.join(parts[1:])}")
            
            self.results['traceroute'] = {
                'success': result.returncode == 0,
                'output': output[:1000],
                'hops': hops[:10],  # First 10 hops
                'hop_count': len(hops)
            }
            
            if hops:
                print(f"{Colors.GREEN}  ✅ Traceroute completed ({len(hops)} hops){Colors.RESET}")
                for i, hop in enumerate(hops[:5], 1):
                    print(f"    {i}. {hop[:50]}")
                if len(hops) > 5:
                    print(f"    ... and {len(hops) - 5} more hops")
            else:
                print(f"{Colors.YELLOW}  ⚠️  No route information{Colors.RESET}")
                
        except subprocess.TimeoutExpired:
            self.results['traceroute'] = {'success': False, 'error': 'Timeout'}
            print(f"{Colors.RED}  ❌ Traceroute timeout{Colors.RESET}")
        except Exception as e:
            self.results['traceroute'] = {'success': False, 'error': str(e)}
            print(f"{Colors.YELLOW}  ⚠️  Traceroute not available: {str(e)[:50]}{Colors.RESET}")
        
        print()
    
    def _scan_target(self, target):
        """Quick port scan"""
        print(f"{Colors.CYAN}🔍 Scanning common ports on {target}...{Colors.RESET}")
        
        # Common ports to scan
        common_ports = [
            21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 
            993, 995, 1723, 3306, 3389, 5432, 5900, 6379, 8080, 8443
        ]
        
        open_ports = []
        
        try:
            # Try nmap first for better results
            if shutil.which('nmap'):
                cmd = ['nmap', '-T4', '-F', target]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                # Parse nmap output
                for line in result.stdout.split('\n'):
                    if '/tcp' in line and 'open' in line:
                        parts = line.split('/')
                        try:
                            port = int(parts[0])
                            service = parts[1].split()[0] if len(parts) > 1 else 'unknown'
                            open_ports.append({'port': port, 'service': service})
                        except:
                            pass
                
                self.results['scan'] = {
                    'method': 'nmap',
                    'open_ports': open_ports,
                    'port_count': len(open_ports),
                    'output': result.stdout[:1000]
                }
                
            # Fallback to socket scan
            else:
                for port in common_ports:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(0.5)
                        result = sock.connect_ex((target, port))
                        if result == 0:
                            try:
                                service = socket.getservbyport(port)
                            except:
                                service = 'unknown'
                            open_ports.append({'port': port, 'service': service})
                        sock.close()
                    except:
                        pass
                
                self.results['scan'] = {
                    'method': 'socket',
                    'open_ports': open_ports,
                    'port_count': len(open_ports),
                    'ports_scanned': len(common_ports)
                }
            
            # Display results
            if open_ports:
                print(f"{Colors.GREEN}  🔓 Open ports found: {len(open_ports)}{Colors.RESET}")
                for port_info in open_ports[:10]:
                    print(f"    Port {port_info['port']}: {port_info.get('service', 'unknown')}")
            else:
                print(f"{Colors.YELLOW}  🔒 No open ports found on common ports{Colors.RESET}")
                
        except subprocess.TimeoutExpired:
            self.results['scan'] = {'success': False, 'error': 'Timeout'}
            print(f"{Colors.RED}  ❌ Port scan timeout{Colors.RESET}")
        except Exception as e:
            self.results['scan'] = {'success': False, 'error': str(e)}
            print(f"{Colors.YELLOW}  ⚠️  Port scan error: {str(e)[:50]}{Colors.RESET}")
        
        print()
    
    def _locate_ip(self, ip):
        """Get IP geolocation"""
        print(f"{Colors.GREEN}📍 Locating IP {ip}...{Colors.RESET}")
        
        try:
            # Try multiple geolocation services
            services = [
                f"http://ip-api.com/json/{ip}",
                f"https://ipapi.co/{ip}/json/",
                f"http://ipwhois.app/json/{ip}"
            ]
            
            location_data = None
            for service_url in services:
                try:
                    response = requests.get(service_url, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        
                        if 'ip-api.com' in service_url:
                            if data.get('status') == 'success':
                                location_data = {
                                    'country': data.get('country', 'N/A'),
                                    'region': data.get('regionName', 'N/A'),
                                    'city': data.get('city', 'N/A'),
                                    'isp': data.get('isp', 'N/A'),
                                    'org': data.get('org', 'N/A'),
                                    'lat': data.get('lat', 'N/A'),
                                    'lon': data.get('lon', 'N/A'),
                                    'timezone': data.get('timezone', 'N/A')
                                }
                                break
                                
                        elif 'ipapi.co' in service_url:
                            if not data.get('error'):
                                location_data = {
                                    'country': data.get('country_name', 'N/A'),
                                    'region': data.get('region', 'N/A'),
                                    'city': data.get('city', 'N/A'),
                                    'isp': data.get('org', data.get('isp', 'N/A')),
                                    'org': data.get('org', 'N/A'),
                                    'lat': data.get('latitude', 'N/A'),
                                    'lon': data.get('longitude', 'N/A'),
                                    'timezone': data.get('timezone', 'N/A')
                                }
                                break
                                
                        elif 'ipwhois.app' in service_url:
                            if not data.get('error'):
                                location_data = {
                                    'country': data.get('country', 'N/A'),
                                    'region': data.get('region', 'N/A'),
                                    'city': data.get('city', 'N/A'),
                                    'isp': data.get('isp', 'N/A'),
                                    'org': data.get('org', 'N/A'),
                                    'lat': data.get('latitude', 'N/A'),
                                    'lon': data.get('longitude', 'N/A'),
                                    'timezone': data.get('timezone', 'N/A')
                                }
                                break
                                
                except:
                    continue
            
            if location_data:
                self.results['location'] = location_data
                
                print(f"{Colors.GREEN}  🌍 Location found:{Colors.RESET}")
                print(f"    Country: {Colors.WHITE}{location_data.get('country', 'N/A')}{Colors.RESET}")
                print(f"    Region:  {Colors.WHITE}{location_data.get('region', 'N/A')}{Colors.RESET}")
                print(f"    City:    {Colors.WHITE}{location_data.get('city', 'N/A')}{Colors.RESET}")
                print(f"    ISP:     {Colors.WHITE}{location_data.get('isp', 'N/A')}{Colors.RESET}")
                if location_data.get('lat') != 'N/A':
                    print(f"    Lat/Lon: {Colors.WHITE}{location_data['lat']}, {location_data['lon']}{Colors.RESET}")
            else:
                self.results['location'] = {'error': 'Could not locate IP'}
                print(f"{Colors.YELLOW}  ⚠️  Could not locate IP address{Colors.RESET}")
                
        except Exception as e:
            self.results['location'] = {'error': str(e)}
            print(f"{Colors.YELLOW}  ⚠️  Location lookup failed: {str(e)[:50]}{Colors.RESET}")
        
        print()
    
    def _get_system_info(self):
        """Get local system information"""
        try:
            system_info = {
                'hostname': socket.gethostname(),
                'os': platform.system(),
                'os_release': platform.release(),
                'python_version': platform.python_version(),
            }
            
            # Get local IP
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                system_info['local_ip'] = s.getsockname()[0]
                s.close()
            except:
                system_info['local_ip'] = '127.0.0.1'
            
            self.results['system'] = system_info
            
        except Exception as e:
            self.results['system'] = {'error': str(e)}
    
    def _save_report(self):
        """Save results to file"""
        try:
            # Create reports directory
            os.makedirs('panda_reports', exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_target = self.results['target'].replace('.', '_').replace(':', '_')
            filename = f"panda_reports/{safe_target}_{timestamp}.json"
            
            # Save JSON report
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            
            self.results['report_file'] = filename
            print(f"{Colors.GREEN}💾 Report saved: {filename}{Colors.RESET}\n")
            
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Could not save report: {e}{Colors.RESET}")
    
    def _print_summary(self):
        """Print comprehensive summary"""
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.WHITE}📋 LAZY PANDA SUMMARY{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
        
        # Target info
        print(f"\n{Colors.YELLOW}🎯 Target:{Colors.RESET} {Colors.WHITE}{self.results['target']}{Colors.RESET}")
        print(f"{Colors.YELLOW}⏰ Time:{Colors.RESET} {Colors.WHITE}{self.results['timestamp']}{Colors.RESET}")
        
        # Ping results
        ping = self.results.get('ping', {})
        ping_status = f"{Colors.GREEN}✓ Success{Colors.RESET}" if ping.get('success') else f"{Colors.RED}✗ Failed{Colors.RESET}"
        print(f"\n{Colors.BLUE}📡 PING:{Colors.RESET} {ping_status}")
        if ping.get('rtt_avg') != 'N/A':
            print(f"   RTT: {ping.get('rtt_avg')} avg, {ping.get('rtt_min')} min, {ping.get('rtt_max')} max")
        
        # Traceroute results
        trace = self.results.get('traceroute', {})
        trace_status = f"{Colors.GREEN}✓ Completed{Colors.RESET}" if trace.get('hop_count', 0) > 0 else f"{Colors.YELLOW}⚠️ No data{Colors.RESET}"
        print(f"\n{Colors.MAGENTA}🛣️  TRACEROUTE:{Colors.RESET} {trace_status}")
        if trace.get('hop_count', 0) > 0:
            print(f"   Hops: {trace.get('hop_count')}")
        
        # Port scan results
        scan = self.results.get('scan', {})
        open_ports = scan.get('open_ports', [])
        scan_status = f"{Colors.GREEN}✓ {len(open_ports)} open ports{Colors.RESET}" if open_ports else f"{Colors.YELLOW}⚠️ No open ports{Colors.RESET}"
        print(f"\n{Colors.CYAN}🔍 PORT SCAN:{Colors.RESET} {scan_status}")
        if open_ports:
            port_list = []
            for port in open_ports[:5]:
                service = port.get('service', 'unknown')
                port_list.append(f"{port['port']}({service})")
            print(f"   {', '.join(port_list)}")
            if len(open_ports) > 5:
                print(f"   ... and {len(open_ports)-5} more")
        
        # Location results
        location = self.results.get('location', {})
        if location and not location.get('error'):
            print(f"\n{Colors.GREEN}📍 LOCATION:{Colors.RESET} {Colors.WHITE}{location.get('city', 'N/A')}, {location.get('country', 'N/A')}{Colors.RESET}")
            print(f"   ISP: {location.get('isp', 'N/A')}")
        
        # System info
        system = self.results.get('system', {})
        print(f"\n{Colors.CYAN}💻 LOCAL SYSTEM:{Colors.RESET}")
        print(f"   Hostname: {system.get('hostname', 'N/A')}")
        print(f"   Local IP: {system.get('local_ip', 'N/A')}")
        
        # Report file
        if 'report_file' in self.results:
            print(f"\n{Colors.GREEN}📁 Full report: {self.results['report_file']}{Colors.RESET}")
        
        print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.GREEN}✅ Lazy Panda completed all tasks!{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")
    
    def check_dependencies(self):
        """Check for required tools"""
        print(f"{Colors.CYAN}🔧 Checking dependencies...{Colors.RESET}")
        
        missing = []
        
        # Check ping
        if shutil.which('ping'):
            print(f"{Colors.GREEN}  ✅ ping{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}  ⚠️  ping not found{Colors.RESET}")
            missing.append('ping')
        
        # Check traceroute/tracepath
        if shutil.which('traceroute') or shutil.which('tracepath'):
            print(f"{Colors.GREEN}  ✅ traceroute{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}  ⚠️  traceroute not found (Windows: built-in){Colors.RESET}")
        
        # Check nmap (optional)
        if shutil.which('nmap'):
            print(f"{Colors.GREEN}  ✅ nmap (faster scanning){Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}  ⚠️  nmap not found (using socket fallback){Colors.RESET}")
        
        if missing:
            print(f"\n{Colors.YELLOW}⚠️  Some tools are missing. Install with:{Colors.RESET}")
            if platform.system().lower() == 'linux':
                print(f"  sudo apt-get install {' '.join(missing)}")
            elif platform.system().lower() == 'darwin':
                print(f"  brew install {' '.join(missing)}")
        
        print()

# =====================
# MAIN ENTRY POINT
# =====================
def main():
    """Main entry point - ONE COMMAND TO RULE THEM ALL"""
    
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Create Lazy Panda
    panda = LazyPanda()
    panda.print_banner()
    
    # Check dependencies
    panda.check_dependencies()
    
    # Check if target provided
    if len(sys.argv) > 1:
        # Command line argument
        target = sys.argv[1]
    else:
        # Interactive mode
        print(f"{Colors.GREEN}🐼 LAZY PANDA - One command does everything!{Colors.RESET}")
        print(f"{Colors.CYAN}Just give me an IP or domain, I'll do the rest:{Colors.RESET}")
        print(f"  • Ping test")
        print(f"  • Traceroute")
        print(f"  • Port scan")
        print(f"  • IP location")
        print()
        
        target = input(f"{Colors.YELLOW}Enter target (IP or domain): {Colors.WHITE}").strip()
        
        if not target:
            print(f"{Colors.RED}❌ No target provided. Exiting.{Colors.RESET}")
            return
    
    # Run everything with one command
    panda.run(target)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}👋 Lazy Panda signing off. Stay lazy!{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()