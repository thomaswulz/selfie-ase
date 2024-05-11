# declare global _start symbol, so the linker can find the entry point
.global _start

# entry point
_start:
	# load counter address
	# note: this expands to two instructions!
    la a1, counter
	
	# critical section start
	# load current counter value
	ld a0, 0(a1)
	# increment register by one
	addi a0, a0, 1
	# store incremented value
	sd a0, 0(a1)
	# critical section end
	# implicit synchronization point here, enforced by stutter logic
	
	# load counter again, since other thread could have changed it
	ld a0, 0(a1)
	
	# exit ecall with counter as exit code
	li a7, 93
    ecall
	

# shared data segment containing the value to increment
.data
    # 64 bit counter, initially 0
    counter: .quad 0
