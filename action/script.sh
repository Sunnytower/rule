git config --local user.email "ljxreal1@gmail.com"
git config --local user.name "Sunnytower"
git status | grep "clean"
  if [[ $? -ne 0 ]]; then
  git add ./*
  git commit -m "update rules" -a
  fi
