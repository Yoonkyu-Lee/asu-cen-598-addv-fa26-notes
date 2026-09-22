# env.cshrc 를 bash 용으로 옮긴 것. 내용은 같고 setenv 만 export 로 바꿨다.
# Apporto 기본 셸이 /bin/bash 라서 env.cshrc 를 그대로 source 하면
# setenv: command not found 가 쏟아지고 VCS 를 못 찾는다.

export PATH=/usr/local2/synopsys/verdi_2024.09/verdi_2024/bin:$PATH
export PATH=/usr/local2/synopsys/vcs_2024/vcs/W-2024.09-SP2-3/bin/:$PATH
export PATH=/usr/local2/synopsys/syn_2023.12-SP51/bin:$PATH

export VCS_HOME=/usr/local2/synopsys/vcs_2024/vcs/W-2024.09-SP2-3
export VERDI_HOME=/usr/local2/synopsys/verdi_2024.09/verdi_2024

export LM_LICENSE_FILE=27020@enlicense5.eas.asu.edu
export SNPSLMD_LICENSE_FILE=27020@enlicense5.eas.asu.edu

export LD_LIBRARY_PATH=/usr/local2/synopsys/verdi_2024.09/verdi_2024/share/PLI/VCS/linux64:/usr/lib64
export LD_LIBRARY_PATH=/usr/local2/synopsys/verdi_2024.09/verdi_2024/platform/linux64/lib/Qt5/lib/depends/xlib:$LD_LIBRARY_PATH

export PDK_DIR=/usr/local2/cadence/NCSU/SRC/FreePDK45
