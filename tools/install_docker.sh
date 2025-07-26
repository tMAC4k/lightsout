#!/bin/bash

# Setup Docker Repository
setup_docker_repo() {
    # Update package index
    sudo apt-get update
    
    # Install packages to allow apt to use a repository over HTTPS
    sudo apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
        
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/raspbian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Set up the stable repository
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/raspbian \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
}

# Install Docker Engine
install_docker_engine() {
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
}

# Post-installation steps
post_install_docker() {
    # Create docker group if it doesn't exist
    sudo groupadd -f docker
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    # Start and enable Docker service
    sudo systemctl start docker
    sudo systemctl enable docker
}

# Main installation function
install_docker() {
    echo "🐳 Installing Docker..."
    
    # Remove old versions
    sudo apt-get remove -y docker docker-engine docker.io containerd runc || true
    
    # Setup repository
    setup_docker_repo
    
    # Install Docker Engine
    install_docker_engine
    
    # Post-installation steps
    post_install_docker
    
    echo "✅ Docker installation completed"
}

# Run installation if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    install_docker
fi
