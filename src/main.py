import os
import subprocess

# GLOBAL VARIABLES 
VM_NAME 	 = "Ubuntu_CSIS_YSU"
ISO_PATH 	 = "ubuntu-24.04.2-live-server-amd64.iso"
NOCLOUD_DIR  = "autoinstall"
NOCLOUD_ISO  = "nocloud.iso"
VM_RAM 		 = 8192  # Ideal 8 GB of RAM for eventual full-GUI Ubuntu
VM_CPUS 	 = 2
VM_DISK 	 = "ubuntu_auto_ysu.vdi"
DISK_SIZE_MB = 50000  # So roughly 50 GB

# SUBPROCESS WRAPPER FUNCTION THINGY
# -----------------------------------
# Shamelessly ripped and modified from Stack Exchange, this is 
# basically just an easier version of the whole subprocess.run thingy 
# so that I don't have to keep adding in quotation marks around every single 
# part of the command I need (you can see this in action in Step 2). 
def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        
        # In case of issue, this will spit out error 
        # message for faulty commands 
        print(f"Error:\n{result.stderr}")
        raise RuntimeError(f"Command failed: {cmd}")
    
    return result.stdout.strip()

# STEP 1: CREATE THE NOCLOUD ISO
# -------------------------------
# It should be noted that for this step to work properly, I had to download 
# the genisoimage package, which will create the nocloud iso so that you  
# can get meta-data and user-data without needing a network service 
def create_nocloud_iso():
    print("Creating nocloud ISO...")
    cmd = f"genisoimage -output {NOCLOUD_ISO} -volid cidata -joliet \
            -rock {NOCLOUD_DIR}/user-data {NOCLOUD_DIR}/meta-data"
    run(cmd)

# STEP 2: CREATE THE VIRTUAL MACHINE
# -----------------------------------
# These next few steps will perform various functions related to the VM
# itself, including proper creation and sizing, creating the virtual 
# drives, etc. 
def create_vm():
    print("Creating VirtualBox VM...")
    
    # This will create the VM and give it the name specified in 
    # the global variables above 
    run(f"VBoxManage createvm \
            --name {VM_NAME} \
            --register")
    
	# This will allocate the appropriate amount of RAM and number
	# of CPUs for the VM, as well as specifying what OS type will
	# be running on the VM (64-bit Ubuntu in this case)
    run(f"VBoxManage modifyvm {VM_NAME} \
			--memory {VM_RAM} \
            --cpus {VM_CPUS} \
            --ostype Ubuntu_64")
    
	# This will use createhd to create the virtual hard drive
	# for the VM. Nothing too fancy, largely just specifying  
	# the size 
    run(f"VBoxManage createhd \
			--filename {VM_DISK} \
            --size {DISK_SIZE_MB}")
    
	# This will give the VM a SATA controller. It will also use
	# an emulated Intel chipset, since I've found that causes the
	# fewest problems with Linux  
    run(f"VBoxManage storagectl {VM_NAME} \
			--name 'SATA Controller' \
        	--add sata \
        	--controller IntelAhci")
    
	# This will attach the vdi to the SATA controller 
    run(f"VBoxManage storageattach {VM_NAME} \
			--storagectl 'SATA Controller' \
        	--port 0 \
        	--device 0 \
        	--type hdd \
        	--medium {VM_DISK}")
    
	# This will add an IDE controller  
    run(f"VBoxManage storagectl {VM_NAME} \
			--name 'IDE Controller' \
            --add ide")
    
	# This will attach the ISO above to the first IDE port as 
	# a dvd drive, and we will use this again a few commands down
	# as the first boot...point or something to try when booting up
    run(f"VBoxManage storageattach {VM_NAME} \
			--storagectl 'IDE Controller' \
            --port 0 \
        	--device 0 \
            --type dvddrive \
            --medium {ISO_PATH}")
    
	# And this will attach the autoinstall's nocloud ISO to the 
	# second dvd port. The nocloud ISO should have the user-data
	# required in order to have our autoinstall YAML file actually
	# install the minimal server setup that we need 
    run(f"VBoxManage storageattach {VM_NAME} \
			--storagectl 'IDE Controller' \
        	--port 1 \
        	--device 0 \
        	--type dvddrive \
            --medium {NOCLOUD_ISO}")
    
	# This activates the network for the VM, which I somehow
    # forgot was a thing you would need to install stuff.
    run(f"VBoxManage modifyvm {VM_NAME} \
            --nic1 nat \
            --cableconnected1 on")
    
	# We need more video memory, or it won't scale properly.
    run(f"VBoxManage modifyvm {VM_NAME} \
            --vram 32")
    
	# This is to enable audio while in the VM
    run(f"VBoxManage modifyvm {VM_NAME} \
            --audioout on \
            --audioin on")

	# Finally, we're going to give the VM a boot order, so
	# that it should try booting from it's "dvd" (which in 
	# this case should hopefully just let it boot from the 
	# Ubuntu autoinstall file)
    run(f"VBoxManage modifyvm {VM_NAME} \
			--boot1 dvd \
            --boot2 disk")

# STEP 3: START THE VIRTUAL MACHINE
# ----------------------------------
# This is just the function that will actually start the VM
# after all else is done. This should make it boot properly
# through the autoinstall file, and you'll end up (I hope) on
# a valid login shell 
def start_vm():
    print("Starting VM...")
    run(f"VBoxManage startvm {VM_NAME} --type gui")

# MAIN FUNCTION
def main():
	# These are just a bunch of failure points in case 
	# something goes wrong, which it totally won't 
    print("You did it!")
    exit(1)

    if not os.path.exists(ISO_PATH):
        print(f"ISO not found: {ISO_PATH}")
        exit(1)
    if not os.path.exists(os.path.join(NOCLOUD_DIR, "user-data")):
        print("Missing user-data")
        exit(1)
    if not os.path.exists(os.path.join(NOCLOUD_DIR, "meta-data")):
        print("Missing meta-data")
        exit(1)

    create_nocloud_iso()
    create_vm()
    start_vm()

if __name__ == "__main__":
	main()
