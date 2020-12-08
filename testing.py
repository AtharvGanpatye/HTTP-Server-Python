import unittest
import requests
import sys

class test (unittest.TestCase):
    def test_get_200(self):
        print("\nTesting GET for existing request..")
        response = requests.get("http://127.0.0.1:8000/index.html")
        try:
            self.assertEqual(response.status_code, 200)
            print("File present on the Server...")
        except:
            print("File not present on the server...")
    
    def test_get_404(self):
        print("\nTesting GET request for non existing file..")
        response = requests.get("http://127.0.0.1:8000/timepass.html")
        try:
            self.assertEqual(response.status_code, 404)
            print("Working Fine for non existing file...")
        except:
            print("Not Working Fine for non existing file...")
    
    def test_get_406(self):
        print("\nTesting GET request for non existing file..")
        headers = {'Accept-Language': 'da'}
        response = requests.get("http://127.0.0.1:8000/timepass.html", headers=headers)
        try:
            self.assertEqual(response.status_code, 406)
            print("Working Fine for languages other than English...")
        except:
            print("Not Working Fine for other Language...")

    def test_get_403(self):
        print("\nTesting GET request for permission not allowed file..")
        response = requests.get("http://127.0.0.1:8000/demo.html")
        try:
            self.assertEqual(response.status_code, 403)
            print("Permissions for File working fine..")
        except:
            print("Not Working Fine for file permissions...")

    def test_head_200(self):
        print("\nTesting HEAD request for existing file..")
        response = requests.head("http://127.0.0.1:8000/index.html")
        try:
            self.assertEqual(response.status_code, 200)
            print("Working Fine for existing file...")
        except:
            print("Not Working Fine for existing file...")

    def test_head_404(self):
        print("\nTesting HEAD request for non existing file..")
        response = requests.head("http://127.0.0.1:8000/random.html")
        try:
            self.assertEqual(response.status_code, 404)
            print("Working Fine for non existing file...")
        except:
            print("Not Working Fine for non existing file...")

    def test_put_201(self):
        print("\nTesting PUT request for adding a File ..")
        response = requests.put("http://127.0.0.1:8000/random.txt", data="This is a testing file")
        try:
            self.assertEqual(response.status_code, 201)
            print("Successfully created a file on the server...")
        except:
            print("File not created ...")


    def test_delete_200(self):
        print("\nTesting DELETE request for a file..")
        response = requests.delete("http://127.0.0.1:8000/uploads/files/temp.txt")
        try:
            self.assertEqual(response.status_code, 200)
            print("Successfully deleted the file on the server...")
        except:
            print("File not deleted ...")

    def test_post_200(self):
        print("\nTesting POST request for a form..")
        response = requests.post("http://127.0.0.1:8000/form.html", data={'name':'Messi', 'age':'32', 'college':'COEP', 'cars':'Volvo', 'info':'Hello World'})
        try:
            self.assertEqual(response.status_code, 200)
            print("Successfully record on the server...")
        except:
            print("Record not added...")


if __name__ == '__main__':
    unittest.main()