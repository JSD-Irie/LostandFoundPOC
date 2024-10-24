using MaterializedViews.Options;
using Microsoft.Azure.Cosmos;
using Microsoft.Extensions.Configuration;
using Azure.Identity;
using System;
using System.Threading.Tasks;

namespace MaterializedViews
{
    internal class Program
    {
        static Database? database;
        static Container? container;

        static string databaseName = "MaterializedViewsDB";
        static string containerName = "LostItems";
        static string partitionKeyPath = "/createUserPlace"; // 小文字スタートで設定

        static async Task Main(string[] args)
        {
            IConfigurationBuilder configuration = new ConfigurationBuilder()
                .AddJsonFile("appsettings.json", optional: true, reloadOnChange: true)
                .AddJsonFile($"appsettings.development.json", optional: true);

            Cosmos? config = configuration
                .Build()
                .Get<Cosmos>();

            Console.WriteLine("This code will generate sample lost items in the MaterializedViewsDB in the LostItems container with a partition key of /createUserPlace.");
            Console.WriteLine("Press any key to continue.");
            Console.ReadKey();

            var accountEndpoint = config?.CosmosUri;
            CosmosClient client = new CosmosClient(accountEndpoint, new DefaultAzureCredential());

            database = await client.CreateDatabaseIfNotExistsAsync(id: databaseName);
            container = await database.CreateContainerIfNotExistsAsync(id: containerName, partitionKeyPath: partitionKeyPath);

            string userInput;
            do
            {
                Console.WriteLine("How many lost items records should be created?");
                userInput = Console.ReadLine()!;

                if (!int.TryParse(userInput, out int numOfLostItems) || numOfLostItems <= 0)
                {
                    Console.WriteLine("Invalid number. Please enter a positive integer.");
                    continue;
                }

                for (int i = 0; i < numOfLostItems; i++)
                {
                    var lostItem = LostItemHelper.GenerateLostItem();

                    if (string.IsNullOrEmpty(lostItem.CreateUserPlace))
                    {
                        Console.WriteLine("Error: CreateUserPlace is not set.");
                        continue;
                    }

                    try
                    {
                        // 動的オブジェクトを使用して Cosmos DB に挿入
                        dynamic itemToInsert = new
                        {
                            id = lostItem.Id,
                            createUserPlace = lostItem.CreateUserPlace,
                            dateFound = lostItem.DateFound,
                            memo = lostItem.Memo,
                            contact = lostItem.Contact,
                            color = lostItem.Color,
                            currency = lostItem.Currency,
                            findPlace = lostItem.FindPlace,
                            imageUrl = lostItem.ImageUrl,
                            isValuables = lostItem.IsValuables,
                            item = lostItem.Item,
                            keyword = lostItem.Keyword,
                            mngmtNo = lostItem.MngmtNo,
                            personal = lostItem.Personal,
                            status = lostItem.Status,
                        };

                        // ここで dynamic を使用
                        ItemResponse<dynamic> response = await container.CreateItemAsync<dynamic>(
                            item: itemToInsert,
                            partitionKey: new PartitionKey(lostItem.CreateUserPlace)
                        );
                        Console.WriteLine($"LostItem created successfully with ID: {response.Resource.id}");
                    }
                    catch (CosmosException ex)
                    {
                        Console.WriteLine($"Error creating LostItem: {ex.StatusCode} - {ex.Message}");
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Unexpected error: {ex.Message}");
                    }
                }

                Console.WriteLine("Add more records? [y/N]");
                userInput = Console.ReadLine()!;
            }
            while (!string.IsNullOrEmpty(userInput) && userInput.Trim().ToUpper() == "Y");

            Console.WriteLine($"Check {containerName} for new LostItems");
            Console.WriteLine("Press Enter to exit.");
            Console.ReadKey();
        }
    }
}
