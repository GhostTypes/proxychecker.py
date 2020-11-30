import os, requests, configparser
from time import sleep
from random import choice
from ctypes import windll
from faker import proxy
from requests import Session
from colorama import Fore, init
from easygui import fileopenbox
from threading import Thread, Lock
from multiprocessing.dummy import Manager, Pool as ThreadPool
from timeit import default_timer as timer


class proxyChecker:
    proxies = []
    checked = 0
    cpm = 0
    bad = 0
    good_http = 0
    good_socks4 = 0
    good_socks5 = 0
    logo = """
██████╗ ██████╗  ██████╗ ██╗  ██╗██╗   ██╗ ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗██████╗    ██████╗ ██╗   ██╗
██╔══██╗██╔══██╗██╔═══██╗╚██╗██╔╝╚██╗ ██╔╝██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝██╔══██╗   ██╔══██╗╚██╗ ██╔╝
██████╔╝██████╔╝██║   ██║ ╚███╔╝  ╚████╔╝ ██║     ███████║█████╗  ██║     █████╔╝ █████╗  ██████╔╝   ██████╔╝ ╚████╔╝ 
██╔═══╝ ██╔══██╗██║   ██║ ██╔██╗   ╚██╔╝  ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██╔══╝  ██╔══██╗   ██╔═══╝   ╚██╔╝  
██║     ██║  ██║╚██████╔╝██╔╝ ██╗   ██║   ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║  ██║██╗██║        ██║   
╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝╚═╝        ╚═╝ """

class Main:
    def __init__(self):
        self.isRunning = False
        self.checkerMode = 'socks4'
        self.checkerSite = 'http://www.google.com'
        self.checkerCode = 200
        self.checkerWait = 5
        self.checkerStart = 0
        self.checkerEnd = 0
        self.checkerThreads = 200
        self.printBad = False
        self.preStart()
        self.startChecker()
        exit()
    
    def preStart(self):
        clear()
        self.setTitle('ProxyChecker v1.3 | Loading')
        print(f'{blue}{proxyChecker.logo}\n\nLoading...')
        self.clearFile('good_http.txt')
        self.clearFile('good_socks4.txt')
        self.clearFile('good_socks5.txt')
        try:
            checkerMode = configLoader.get('Config', 'check_mode')
            if checkerMode in ['http', 'socks4', 'socks5']:
                self.checkerMode = checkerMode
            else:
                print(f'{red}[{white}!{red}] Invalid checker mode, Quitting.')
                exit()
        except:
            print(f'{red}[{white}!{red}] Error loading checker mode, Quitting.')
            exit()
        try:
            checkerSite = configLoader.get('Config', 'check_site')
            self.checkerSite = checkerSite
        except:
            print(f'{red}[{white}!{red}] Error loading checker site, Quitting.')
            exit()
        try:
            checkerTime = configLoader.getint('Config', 'check_time')
            self.checkerWait = checkerTime
        except:
            print(f'{red}[{white}!{red}] Error loading checker timeout, Quitting.')
            exit()
        try:
            checkerCode = configLoader.getint('Config', 'check_code')
            self.checkerCode = checkerCode
        except:
            print(f'{red}[{white}!{red}] Error loading checker success code, Quitting.')
            exit()
        try:
            printBad = configLoader.getboolean('Config', 'print_bad')
            self.printBad = printBad
        except:
            print(f'{red}[{white}!{red}] Error loading print bad, Quitting.')
            exit()
        try:
            checkThreads = configLoader.getint('Config', 'check_threads')
            self.checkerThreads = checkThreads
        except:
            print(f'{red}[{white}!{red}] Error loading checker threads, Quitting.')
            exit()
        sleep(2)
        clear()
        print(f'{blue}[ProxyChecker v1.3 | Summary]')
        print(f'{blue}Check Mode: {white}{self.checkerMode}')
        print(f'{blue}Check Site: {white}{self.checkerSite}')
        print(f'{blue}Check Threads: {white}{self.checkerThreads}')
        print(f'{blue}Check Timeout: {white}{self.checkerWait}')
        print(f'{blue}Check Success Code: {white}{self.checkerCode}')
        pBad = f'{red}No'
        if self.printBad:
            pBad = f'{green}Yes'
        print(f'{blue}Show Bad Proxies: {pBad}')


    def startChecker(self):
        print(f'\n\n{yellow}[{white}i{yellow}] Press [Enter] to load proxies.')
        w = input('')
        clear()
        self.loadProxies()
        self.setTitle('ProxyChecker v1.3 | Starting')
        self.isRunning = True
        Thread(target=self.cpmTracker, daemon=True).start()
        print(f'{blue}Starting Proxy Checker with {white}{self.checkerThreads}{blue} threads.')
        mainpool = ThreadPool(processes=self.checkerThreads)
        clear()
        print(f'{blue}{proxyChecker.logo}\n\n')
        if self.checkerMode == 'http':
            self.checkerStart = timer()
            mainpool.imap_unordered(func=self.checkHttp, iterable=proxyChecker.proxies)
            Thread(target=self.titleManager).start()
            mainpool.close()
            mainpool.join()
            self.checkerEnd = timer()
            rGood = proxyChecker.good_http
        elif self.checkerMode == 'socks4':
            self.checkerStart = timer()
            mainpool.imap_unordered(func=self.checkSocks4, iterable=proxyChecker.proxies)
            Thread(target=self.titleManager).start()
            mainpool.close()
            mainpool.join()
            self.checkerEnd = timer()
            rGood = proxyChecker.good_socks4
        elif self.checkerMode == 'socks5':
            self.checkerStart = timer()
            mainpool.imap_unordered(func=self.checkSocks5, iterable=proxyChecker.proxies)
            Thread(target=self.titleManager).start()
            mainpool.close()
            mainpool.join()
            self.checkerEnd = timer()
            rGood = proxyChecker.good_socks5
        else:
            clear()
            print(f'{red}[{white}!{red}] Invalid checkerMode during startChecker()! Should never happen...')
            exit()
        clear()
        self.isRunning = False
        sleep(0.5)
        self.setTitle('ProxyChecker v1.3 | Finished Checking')
        print(f'{green}{proxyChecker.logo}\n\nFinished!')
        print(f'{green}Working: {rGood} ({self.percentage(rGood, proxyChecker.checked)}%)')
        print(f'{red}Dead: {proxyChecker.bad} ({self.percentage(proxyChecker.bad, proxyChecker.checked)}%)')
        print(f'{blue}Checking {white}{proxyChecker.checked}{blue} proxies took {white}{self.convertSec(self.checkerEnd - self.checkerStart)}.')

    def percentage(self, part, whole):
        return round(100 * float(part)/float(whole))

    def clearFile(self, file):
        with open(file, 'w') as f:
            f.write('')

    def titleManager(self):
        while self.isRunning:
            timeNow = timer()
            runTime = self.convertSec(timeNow - self.checkerStart)
            #runTime = self.convertSec(runTime)
            if self.checkerMode == 'socks4':
                title = (
                    f'ProxyChecker v1.3 | Checking SOCKS4'
                    f' | ({proxyChecker.checked}/{len(proxyChecker.proxies)}) ({self.percentage(proxyChecker.checked, len(proxyChecker.proxies))}%)'
                    f' | CPM: {proxyChecker.cpm}'
                    f' | Working: {proxyChecker.good_socks4}'
                    f' | Dead: {proxyChecker.bad}'
                    f' | Time Elapsed: {runTime}'
                )
            elif self.checkerMode == 'socks5':
                title = (
                    f'ProxyChecker v1.3 | Checking SOCKS5'
                    f' | ({proxyChecker.checked}/{len(proxyChecker.proxies)}) ({self.percentage(proxyChecker.checked, len(proxyChecker.proxies))}%)'
                    f' | CPM: {proxyChecker.cpm}'
                    f' | Working: {proxyChecker.good_socks5}'
                    f' | Dead: {proxyChecker.bad}'
                    f' | Time Elapsed: {runTime}'
                )
            elif self.checkerMode == 'http':
                title = (
                    f'ProxyChecker v1.3 | Checking HTTP'
                    f' | ({proxyChecker.checked}/{len(proxyChecker.proxies)}) ({self.percentage(proxyChecker.checked, len(proxyChecker.proxies))}%)'
                    f' | CPM: {proxyChecker.cpm}'
                    f' | Working: {proxyChecker.good_http}'
                    f' | Dead: {proxyChecker.bad}'
                    f' | Time Elapsed: {runTime}'
                )
            else:
                lock.acquire()
                print(f'{red}[Error]{white} Invalid Checker Mode.')
                exit()
            self.setTitle(title)

    def setTitle(self, title):
        windll.kernel32.SetConsoleTitleW(title)
    
    def convertSec(self, seconds):
        seconds = round(seconds)
        seconds = seconds % (24 * 3600) 
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return "%d:%02d:%02d" % (hour, minutes, seconds)

    def cpmTracker(self):
        while self.isRunning:
            if proxyChecker.checked >= 1:
                now = proxyChecker.checked
                sleep(3)
                proxyChecker.cpm = (proxyChecker.checked - now) * 20
    
    def loadProxies(self):
        self.setTitle('Load your proxies')
        while True:
            try:
                clear()
                print(f'{blue}{proxyChecker.logo}\n\n')
                print(f'{yellow}[{white}i{yellow}]{white} Load your proxies.')
                sleep(0.3)
                loader = open(fileopenbox(title="Load your proxies", default="*.txt"), 'r', encoding="utf8", errors='ignore').read().split('\n')
                proxyChecker.proxies = list(set(x.strip() for x in loader if x != ''))
                if len(proxyChecker.proxies) == 0:
                    clear()
                    print(f'{red}{proxyChecker.logo}\n\n')
                    print(f'{red}[{white}!{red}] File is empty.')
                    sleep(2)
                    continue
                clear()
                print(f'{green}{proxyChecker.logo}\n\n')
                print(f"{green}[{white}+{green}]{white} Loaded {green}{len(proxyChecker.proxies)}{white} proxies.")
                sleep(3)
                break
            except:
                exit()
        clear()

    def formatProxy(self, proxy, type):
        return {'http': f"{type}://{proxy}", 'https': f"{type}//{proxy}"}

    def httpCheck(self, proxy):
        site = self.checkerSite
        code = self.checkerCode
        wait = self.checkerWait
        broxy = self.formatProxy(proxy, type='http')
        try:
            r = requests.get(url=site, proxies=broxy, timeout=wait)
            if r.status_code == code:
                return True
            else:
                return False
        except:
            return False
    
    def socks4Check(self, proxy):
        site = self.checkerSite
        code = self.checkerCode
        wait = self.checkerWait
        broxy = self.formatProxy(proxy, type='socks4')
        try:
            r = requests.get(url=site, proxies=broxy, timeout=wait)
            if r.status_code == code:
                return True
            else:
                return False
        except:
            return False

    def socks5Check(self, proxy):
        site = self.checkerSite
        code = self.checkerCode
        wait = self.checkerWait
        broxy = self.formatProxy(proxy, type='socks5')
        try:
            r = requests.get(url=site, proxies=broxy, timeout=wait)
            if r.status_code == code:
                return True
            else:
                return False
        except:
            return False

    def checkHttp(self, proxy):
        pCheck = self.httpCheck(proxy)
        if pCheck:
            proxyChecker.good_http += 1
            self.safePrint(f'{green}[{white}+{green}] HTTP: {proxy}')
            self.writeHit(pType=1, proxy=proxy)
        else:
            proxyChecker.bad += 1
            if self.printBad:
                self.safePrint(f'{red}[{white}+{red}] Dead: {proxy}')
        proxyChecker.checked += 1
            
    def checkSocks4(self, proxy):
        pCheck = self.socks4Check(proxy)
        if pCheck:
            proxyChecker.good_socks4 += 1
            self.safePrint(f'{green}[{white}+{green}] SOCKS4: {proxy}')
            self.writeHit(pType=2, proxy=proxy)
        else:
            proxyChecker.bad += 1
            if self.printBad:
                self.safePrint(f'{red}[{white}+{red}] Dead: {proxy}')
        proxyChecker.checked += 1

    def checkSocks5(self, proxy):
        pCheck = self.socks5Check(proxy)
        if pCheck:
            proxyChecker.good_socks5 += 1
            self.safePrint(f'{green}[{white}+{green}] SOCKS5: {proxy}')
            self.writeHit(pType=1, proxy=proxy)
        else:
            proxyChecker.bad += 1
            if self.printBad:
                self.safePrint(f'{red}[{white}+{red}] Dead: {proxy}')
        proxyChecker.checked += 1

    def safePrint(self, line):
        lock.acquire()
        print(line)
        lock.release()

    def writeHit(self, pType, proxy):
        lock.acquire()
        outFile = ''
        if pType == 1:
            outFile = 'good_http.txt'
        elif pType == 2:
            outFile = 'good_socks4.txt'
        elif pType == 3:
            outFile = 'good_socks5.txt'
        else:
            outFile = ''
            print(f'{yellow}[Debug] Invalid pType passed to writeHit ({pType}), unable to process hit.')
        try:
            with open(outFile, 'a') as outF:
                outF.write(f'{proxy}\n')
        except:
            print(f'{yellow}[Debug] Failed to write hit, Type: {pType}, Proxy: {proxy}, Out File: {outFile}')
        lock.release()

if __name__ == '__main__':
    init()
    clear = lambda: os.system('cls')
    lock = Lock()
    yellow = Fore.LIGHTYELLOW_EX
    red = Fore.LIGHTRED_EX
    green = Fore.LIGHTGREEN_EX
    cyan = Fore.LIGHTCYAN_EX
    blue = Fore.LIGHTBLUE_EX
    white = Fore.LIGHTWHITE_EX
    magenta = Fore.LIGHTMAGENTA_EX
    configLoader = configparser.RawConfigParser()
    try:
        configLoader.read(r'ProxyChecker.cfg')
    except:
        print(f'{red}[{white}!{red}] Unable to load config, Quitting.')
        exit()
    Main()