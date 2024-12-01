# -*- coding: utf-8 -*
#!/usr/bin/python
#https://github.com/Jenderal92/reverse-ip-new-api
import requests
import xml.etree.ElementTree as ET
from multiprocessing.dummy import Pool as ThreadPool

def display_b():
    print("=" * 50)
    print(" " * 10 + "Reverse IP | Shin Code")
    print(" " * 10 + "Created by Python 2.7")
    print("=" * 50)
    print("\n")

def reverse_ip(base_url, ip, initial_domain):
    try:
        reverse_domain = initial_domain
        all_domains = set()
        has_more = True

        while has_more:
            params = {
                'threepointoneipnum': ip,
                'reverse_domain': reverse_domain
            }
            response = requests.get(base_url, params=params, timeout=10)
            if response.status_code != 200:
                print("[ERROR] Failed to fetch data for: {}".format(initial_domain))
                return all_domains

            root = ET.fromstring(response.content)
            result = root.find('result').text
            if result != 'ok':
                print("[ERROR] API returned an error for: {}".format(initial_domain))
                return all_domains
            for child in root:
                if child.tag.startswith('domain_'):
                    domain = child.text.strip()
                    if domain not in all_domains:
                        all_domains.add(domain)

            has_more = root.find('has_more').text == '1'
            if has_more:
                reverse_domain = root.find('last_domain_punycode').text
            else:
                break

        return all_domains

    except Exception as e:
        print("[ERROR] Exception for: {} - {} ".format(initial_domain, str(e)))
        return set()

def generate_threepointoneipnum(domain):
    parts = domain.split('.')
    formatted_parts = ["%03d" % int(part) for part in parts]
    return "_{}".format("".join(formatted_parts))
    
    
def process_domain(domain):
    base_url = "https://atsameip.intercode.ca/xmlloadIPpage2.php"
    ip = threepointoneipnum = generate_threepointoneipnum(domain)
    print("[INFO] Threepointoneipnum : {} ".format(ip))
    print("[INFO] Scanning domain: {} ".format(domain))
    found_domains = reverse_ip(base_url, ip, domain)
    print("[INFO] Found {} domains for {}".format(len(found_domains), domain))
    return found_domains


def main():
    display_b()
    try:
        list_file = raw_input("Enter list.txt: ").strip()
        with open(list_file, 'r') as f:
            domain_list = f.read().splitlines()
        max_threads = int(raw_input("Enter number of threads (e.g., 10): "))
        pool = ThreadPool(max_threads)
        results = pool.map(process_domain, domain_list)

        all_results = set()
        for res in results:
            all_results.update(res)
        with open("result.txt", "w") as result_file:
            for domain in sorted(all_results):
                result_file.write(domain + "\n")

        print("\n[INFO] Total unique domains found: {} ".format(len(all_results)))
        print("[INFO] Results saved to result.txt")

        pool.close()
        pool.join()

    except Exception as e:
        print("[ERROR] Main function failed: {}".format(str(e)))


if __name__ == '__main__':
    main()
