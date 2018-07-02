#!/usr/bin/env bash

replace_str1="_Volumes_Mac HD_data_Files_eclipse_workspace_workspace_work_minicondas_4_4_10_envs_eman-deps-11-gui_bin_"
replace_str2="/Volumes/Mac HD/data/Files/eclipse_workspace/workspace_work/minicondas/4.4.10/envs/eman-deps-11-gui/bin/"

IFS=','
for f in `ls -m "docs/${replace_str1}"*`;do
    ff=$(echo "$f" | tr -d '\n')
    ff=${ff# }
    ff2=${ff/${replace_str1}/}
    mv -v "$ff" $ff2
done

sed -i.bak -e "s/${replace_str1}//g" docs/index.html docs/status.json docs/*.html
rm docs/*.bak

sed -i.bak -e "s?${replace_str2}??g" docs/index.html docs/status.json docs/*.html
rm docs/*.bak
