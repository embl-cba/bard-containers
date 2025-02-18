if [ ! -d ~/.config ]; then
        echo "create  ~/.config  directory"
        mkdir -p ~/.config
        cp -r /composer/.config ~/.config
fi

if [ ! -d ~/.config/gtk-3.0 ]; then
        echo "create  ~/.config/gtk-3.0 directory"
        mkdir -p ~/.config/gtk-3.0
        cp -r /composer/.config/gtk-3.0 ~/.config/gtk-3.0 
fi

if [ ! -f ~/.config/gtk-3.0/settings.ini ]; then
        echo "copy ~/.config/gtk-3.0/settings.ini file"
        cp /composer/.config/gtk-3.0/settings.ini ~/.config/gtk-3.0 
fi
