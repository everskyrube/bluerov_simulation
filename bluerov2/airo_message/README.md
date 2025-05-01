# AIRO_LAB Messages
These are some common Robot messages that are frequently utilized for control and estimation. Usually served as submodules in our various repos.

### Add Submodules
```
git submodule add https://github.com/HKPolyU-UAV/airo_message.git 
git submodule add https://github.com/pattylo/ros_utilities.git 
git submodule update --init --recursive
```

### Remove Submodules (A bit troublesome)
First, delete the relevant section from .git/config. Then,
```
git rm --cached {path_to_submodule}
rm -rf .git/modules/{path_to_submodule}
rm -rf {path_to_submodule}
```

### Maintainer
[Patrick Lo](https://github.com/pattylo), AIRo-Lab, RCUAS, PolyU: patty.lo@connect.polyu.hk <br/> 
[RockyJBL](https://github.com/RockyJBL) @ AIRO-LAB @ RCUAS, HKPolyU <br>
