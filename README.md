# AutoRig 🛠️

**AutoRig** is a powerful, declarative development environment bootstrapper for Linux. Stop wasting time manually running `apt install`, cloning repos, and linking dotfiles every time you set up a new machine or project. Define your rig in a YAML file, and let AutoRig handle the rest.

![License](https://img.shields.io/github/license/Dacraezy1/autorig)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)

## 🚀 Features

*   **Declarative Configuration:** Define your tools, packages, and repos in a simple `rig.yaml` file.
*   **Multi-Distro Support:** Smart detection for `apt`, `dnf`, `pacman`, and `yay`.
*   **Git Operations:** Automatically clone repositories and checkout specific branches.
*   **Dotfile Management:** Symlink your config files to the right locations.
*   **Modular:** Extensible architecture allows for adding custom installers.

## 📦 Installation

```bash
git clone https://github.com/Dacraezy1/autorig.git
cd autorig
pip install -e .
```

## ⚡ Usage

1.  Create a `rig.yaml` file (see `rig.example.yaml`).
2.  Run AutoRig:

```bash
autorig apply rig.yaml
```

## 📝 Example Configuration

```yaml
name: "Python Dev Rig"
system:
  packages:
    - git
    - vim
    - htop
    - python3-venv

git:
  repositories:
    - url: "https://github.com/Dacraezy1/autorig"
      path: "~/projects/autorig"

dotfiles:
  - source: "./configs/.vimrc"
    target: "~/.vimrc"
```

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## 👤 Author

**Dacraezy1**
*   GitHub: [@Dacraezy1](https://github.com/Dacraezy1)
*   Email: younesaouzal18@gmail.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
