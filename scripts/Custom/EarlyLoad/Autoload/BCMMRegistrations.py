# Print BCMM version
# noinspection PyUnresolvedReferences
import bcmm_version

# it's a secret :D

# Wwant to check if BCMM is present try?
try:
	import bcmm_version
except:
	print("No BCMM signature file")
# Want to check if you have a specific version?
import bcmm_version
v = bcmm_version.version # 0.3.23-alpha at the time of writing this

# Check version cmp(v, target version)
print(cmp(v, "0.2"))
# output 1 = means version 0.3.23-alpha is greater than 0.2
print(cmp(v, "0.3"))
# output 1 = means version 0.3.23-alpha is greater than 0.3
print(cmp(v, "0.3.23-alpha"))
# output 0 = means versions are the same
print(cmp(v, "0.3.23-beta"))
# output -1 = means 0.3.23-beta is greater than 0.3-23-alpha (alpha < beta < rc < no alpha\beta\rc)
print(cmp(v, "0.4"))
# output -1 = means 0.4 is greater than 0.3.23-alpha