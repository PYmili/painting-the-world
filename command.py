import os
import argparse
import painting_the_world

def main():
    parser = argparse.ArgumentParser(description="Painting the world tool")

    parser.add_argument('-f', '--file_path', type=str, default=None, help='Path to the image file')
    parser.add_argument('-x', '--base-x', type=int, default=0, help='Base x-coordinate for painting')
    parser.add_argument('-y', '--base-y', type=int, default=100, help='Base y-coordinate for painting')
    parser.add_argument('-z', '--base-z', type=int, default=0, help='Base z-coordinate for painting')
    parser.add_argument('-c', '--color-space', choices=['rgb', 'lab', 'hsv', 'yiq', 'ycbcr'], default='rgb', help='Color space for matching')
    parser.add_argument('--no-save', action='store_false', dest='is_save', help='Disable saving the generated painting')
    parser.add_argument('-d', '--delete-generated', action='store_true', help='Delete the generated painting')
    parser.add_argument('-g', '--generate', action='store_true', help='Generate a painting')
    parser.add_argument('-rm', '--resize-multiple', type=int, help='Resize multiple for image processing')

    args = parser.parse_args()

    host = '127.0.0.1'
    port = 25575
    password = 'rcon_pwd'

    with painting_the_world.Painting(host, port, passwd=password) as client:
        if not args.file_path:
            print("Error: Please specify the path to the image file using -f option.")
            exit(1)

        client.set(
            args.file_path,
            args.base_x, args.base_y, args.base_z,
            args.color_space, args.is_save, args.resize_multiple
        )
        if args.generate:
            client.generate()    
        elif args.delete_generated:
            client.delete_generated()
        elif args.file_path:
            print("Error: Please specify a command or use -g option to generate the painting.")

if __name__ == "__main__":
    main()
